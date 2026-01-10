"use client";

import { useState, useEffect } from "react";
import {
  Search,
  Plus,
  Edit2,
  Eye,
  Building2,
  DollarSign,
  Cloud,
  Loader2,
  Trash2,
  User as UserIcon,
  Shield,
  Key
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useAuth } from "@/contexts/AuthContext";
import { clientsService } from "@/lib/services/clients";
import { authService } from "@/lib/services/auth";
import { Client } from "@/types/dashboard";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

const formSchema = z.object({
  name: z.string().min(2, "Client name must be at least 2 characters"),
  email: z.string().email().optional().or(z.literal("")),
  password: z.string().min(8, "Password must be at least 8 characters").optional().or(z.literal("")),

  // CPM
  surfsideCpm: z.string().optional(),
  facebookCpm: z.string().optional(),

  // S3 Credentials
  s3BucketName: z.string().optional(),
  s3Region: z.string().optional(),
  s3AccessKeyId: z.string().optional(),
  s3SecretAccessKey: z.string().optional(),
  status: z.boolean().optional(),
});

// Component to fetch and display CPM for a client/source
const CpmCell = ({ clientId, source }: { clientId: string, source: "surfside" | "facebook" }) => {
  const { data: settings } = useQuery({
    queryKey: ["client-settings", clientId],
    queryFn: () => clientsService.getCpmSettings(clientId),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const cpm = settings?.find((s) => s.source === source)?.cpm;

  return (
    <span className="font-mono text-sm">
      {cpm ? `$${Number(cpm).toFixed(2)}` : "—"}
    </span>
  );
};

export default function AdminClients() {
  const [searchQuery, setSearchQuery] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);

  // Delete Dialog State
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [clientToDelete, setClientToDelete] = useState<Client | null>(null);

  const { simulateAsClient, simulatedClient, isAdmin } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  // Redirect if viewing as client
  useEffect(() => {
    if (simulatedClient && isAdmin) {
      router.push("/dashboard");
    }
  }, [simulatedClient, isAdmin, router]);

  const { data: clientsData, isLoading } = useQuery({
    queryKey: ["admin", "clients"],
    queryFn: () => clientsService.getClients(0, 100),
  });

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      surfsideCpm: "",
      facebookCpm: "",
      s3BucketName: "",
      s3Region: "us-east-1",
      s3AccessKeyId: "",
      s3SecretAccessKey: "",
    },
  });

  // Fetch settings when editing
  const { data: editingSettings } = useQuery({
    queryKey: ["client-settings", editingClient?.id],
    queryFn: () => clientsService.getCpmSettings(editingClient!.id),
    enabled: !!editingClient,
  });

  // Reset/Populate form
  useEffect(() => {
    if (isDialogOpen) {
      if (editingClient) {
        // Pre-fill form from editingClient
        const surfside = editingSettings?.find(s => s.source === "surfside")?.cpm;
        const facebook = editingSettings?.find(s => s.source === "facebook")?.cpm;

        form.reset({
          name: editingClient.name,
          email: "", // User fetch logic skipped for simplicity as per requirement
          password: "",
          surfsideCpm: surfside ? String(surfside) : "",
          facebookCpm: facebook ? String(facebook) : "",
          s3BucketName: "",
          s3Region: "us-east-1",
          s3AccessKeyId: "",
          s3SecretAccessKey: "",
          status: editingClient.status === 'active',
        });
      } else {
        form.reset({
          name: "",
          email: "",
          password: "",
          surfsideCpm: "",
          facebookCpm: "",
          s3BucketName: "",
          s3Region: "us-east-1",
          s3AccessKeyId: "",
          s3SecretAccessKey: "",
          status: true,
        });
      }
    }
  }, [isDialogOpen, editingClient, editingSettings, form]);

  // --- Mutations ---

  const createClientMutation = useMutation({
    mutationFn: clientsService.createClient,
  });

  const registerUserMutation = useMutation({
    mutationFn: authService.register,
  });

  const updateClientMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => clientsService.updateClient(id, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin", "clients"] });
      await queryClient.invalidateQueries({ queryKey: ["clients"] });
      toast.success("Client updated successfully");
      setIsDialogOpen(false);
      setEditingClient(null);
      form.reset();
    },
    onError: (error) => toast.error("Failed to update client")
  });

  const saveCpmMutation = useMutation({
    mutationFn: ({ clientId, source, cpm }: { clientId: string, source: "surfside" | "facebook", cpm: number }) =>
      clientsService.updateCpmSetting(clientId, { source, cpm }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["client-settings", variables.clientId] });
    }
  });

  const deleteClientMutation = useMutation({
    mutationFn: clientsService.deleteClient,
  });

  const deleteUserMutation = useMutation({
    mutationFn: authService.deleteUser,
  });

  // --- Handlers ---

  const syncCpms = async (clientId: string, values: z.infer<typeof formSchema>) => {
    const promises = [];
    if (values.surfsideCpm) {
      promises.push(saveCpmMutation.mutateAsync({
        clientId, source: "surfside", cpm: parseFloat(values.surfsideCpm)
      }));
    }
    if (values.facebookCpm) {
      promises.push(saveCpmMutation.mutateAsync({
        clientId, source: "facebook", cpm: parseFloat(values.facebookCpm)
      }));
    }
    await Promise.all(promises);
  };

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    try {
      if (editingClient) {
        // Update Client
        await updateClientMutation.mutateAsync({
          id: editingClient.id,
          data: {
            name: values.name,
            status: values.status ? 'active' : 'disabled'
          }
        });
        await syncCpms(editingClient.id, values);
      } else {
        // Create Flow
        if (!values.email || !values.password) {
          toast.error("Email and Password are required for new clients");
          return;
        }

        // 1. Create User
        const newUser = await registerUserMutation.mutateAsync({
          email: values.email,
          password: values.password,
          role: "client"
        });

        if (!newUser?.id) throw new Error("Failed to create user");

        // 2. Create Client
        const newClient = await createClientMutation.mutateAsync({
          name: values.name,
          user_id: newUser.id
        });

        // 3. Settings
        await syncCpms(newClient.id, values);

        await queryClient.invalidateQueries({ queryKey: ["admin", "clients"] });
        await queryClient.invalidateQueries({ queryKey: ["clients"] });
        toast.success("Client created successfully");
        setIsDialogOpen(false);
      }
    } catch (error: any) {
      console.error("Error submitting form", error);
      toast.error(error.message || "Failed to process request");
    }
  };

  const handleDelete = async () => {
    if (!clientToDelete) return;

    try {
      const userId = clientToDelete.userId;

      // 1. Delete Client (Must be first due to FK constraints if client points to user, or user points to client? 
      // Actually DB schema: clients.user_id -> users.id (RESTRICT). 
      // So we must delete CLIENT first to free the User.
      // 1. Delete Client (Backend now handles cascading user deletion)
      await deleteClientMutation.mutateAsync(clientToDelete.id);

      // 2. Notify success
      if (userId && clientToDelete.userRole !== 'admin') {
        toast.success("Client and associated user deleted");
      } else {
        toast.success("Client deleted");
      }

      await queryClient.invalidateQueries({ queryKey: ["admin", "clients"] });
      await queryClient.invalidateQueries({ queryKey: ["clients"] });
      setIsDeleteDialogOpen(false);
      setClientToDelete(null);
    } catch (error) {
      console.error("Delete failed", error);
      toast.error("Failed to delete client or associated user");
    }
  };

  const filteredClients = clientsData?.clients.filter((client) =>
    client.name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const handleSimulate = (client: Client) => {
    simulateAsClient(client);
    router.push("/dashboard");
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Client Management
          </h1>
          <p className="text-slate-600">
            Manage client accounts and configurations
          </p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button
              variant="gold"
              className="gap-2 cursor-pointer"
              onClick={() => {
                setEditingClient(null);
              }}
            >
              <Plus className="w-4 h-4" />
              Add Client
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-white max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingClient ? "Edit Client" : "Add New Client"}
              </DialogTitle>
              <DialogDescription>
                {editingClient ? "Update client settings." : "Create a new client account, user login, and settings."}
              </DialogDescription>
            </DialogHeader>

            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">

                <Tabs defaultValue="profile" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="profile">Profile</TabsTrigger>
                    <TabsTrigger value="cpm">CPM Settings</TabsTrigger>
                    <TabsTrigger value="credentials">Credentials</TabsTrigger>
                  </TabsList>

                  {/* Tab 1: Profile */}
                  <TabsContent value="profile" className="space-y-4 pt-4">
                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Client Name <span className="text-red-500">*</span></FormLabel>
                          <FormControl>
                            <Input placeholder="Acme Corp" className="bg-white" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {!editingClient && (
                      <>
                        <div className="grid grid-cols-2 gap-4">
                          <FormField
                            control={form.control}
                            name="email"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Email (for Login) <span className="text-red-500">*</span></FormLabel>
                                <FormControl>
                                  <Input placeholder="client@example.com" className="bg-white" {...field} />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                          <FormField
                            control={form.control}
                            name="password"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Password <span className="text-red-500">*</span></FormLabel>
                                <FormControl>
                                  <Input type="password" placeholder="********" className="bg-white" {...field} />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </div>
                        <div className="bg-blue-50 p-3 rounded-md flex gap-2 text-sm text-blue-700">
                          <UserIcon className="w-4 h-4 mt-0.5 shrink-0" />
                          <p>This will create a new user account with the "Client" role.</p>
                        </div>
                      </>
                    )}
                    {editingClient && (
                      <div className="space-y-4">
                        <FormField
                          control={form.control}
                          name="status"
                          render={({ field }) => (
                            <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4 bg-white">
                              <div className="space-y-0.5">
                                <FormLabel className="text-base">Active Status</FormLabel>
                                <div className="text-sm text-slate-500">
                                  {field.value ? "Client can access the platform" : "Client access is disabled"}
                                </div>
                              </div>
                              <FormControl>
                                <Switch
                                  checked={field.value}
                                  onCheckedChange={field.onChange}
                                />
                              </FormControl>
                            </FormItem>
                          )}
                        />

                      </div>
                    )}
                  </TabsContent>

                  {/* Tab 2: CPM */}
                  <TabsContent value="cpm" className="space-y-4 pt-4">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
                        <DollarSign className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-slate-900">CPM Configuration</h3>
                        <p className="text-xs text-slate-600">Set cost per mille for each data source</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="surfsideCpm"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>CTV CPM</FormLabel>
                            <FormControl>
                              <div className="relative">
                                <DollarSign className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
                                <Input type="number" step="0.01" placeholder="0.00" className="pl-9 bg-white" {...field} />
                              </div>
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="facebookCpm"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Facebook CPM</FormLabel>
                            <FormControl>
                              <div className="relative">
                                <DollarSign className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
                                <Input type="number" step="0.01" placeholder="0.00" className="pl-9 bg-white" {...field} />
                              </div>
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </TabsContent>

                  {/* Tab 3: Credentials */}
                  <TabsContent value="credentials" className="space-y-4 pt-4">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
                        <Cloud className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-slate-900">S3 Configuration</h3>
                        <p className="text-xs text-slate-600">Optional credentials for CTV data sync</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="s3BucketName"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Bucket Name</FormLabel>
                            <FormControl><Input placeholder="my-bucket" className="bg-white" {...field} /></FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="s3Region"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Region</FormLabel>
                            <FormControl>
                              <select {...field} className="w-full h-10 px-4 rounded-lg border border-slate-200 bg-white text-slate-900 text-sm">
                                <option value="us-east-1">US East (N. Virginia)</option>
                                <option value="us-west-2">US West (Oregon)</option>
                              </select>
                            </FormControl>
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="s3AccessKeyId"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Access Key ID</FormLabel>
                            <FormControl><Input type="password" placeholder="Access Key" className="bg-white" {...field} /></FormControl>
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="s3SecretAccessKey"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Secret Access Key</FormLabel>
                            <FormControl><Input type="password" placeholder="Secret Key" className="bg-white" {...field} /></FormControl>
                          </FormItem>
                        )}
                      />
                    </div>
                  </TabsContent>
                </Tabs>

                <div className="flex justify-end gap-2 pt-4 border-t border-slate-200">
                  <Button type="button" variant="ghost" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                  <Button type="submit" variant="gold" disabled={createClientMutation.isPending || updateClientMutation.isPending || registerUserMutation.isPending}>
                    {(createClientMutation.isPending || updateClientMutation.isPending || registerUserMutation.isPending) && (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    )}
                    {editingClient ? "Save Changes" : "Create Client"}
                  </Button>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600" />
          <Input placeholder="Search clients..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-10" />
        </div>
      </div>

      <div className="bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Loading clients...</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent border-b border-slate-200">
                <TableHead className="font-bold text-slate-900 px-4 py-3">Client</TableHead>
                <TableHead className="font-bold text-slate-900 px-4 py-3 text-center">Status</TableHead>
                <TableHead className="font-bold text-slate-900 px-4 py-3 text-center">CTV CPM</TableHead>
                <TableHead className="font-bold text-slate-900 px-4 py-3 text-center">Facebook CPM</TableHead>
                <TableHead className="font-bold text-slate-900 px-4 py-3">Created</TableHead>
                <TableHead className="font-bold text-slate-900 px-4 py-3 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredClients.length === 0 ? (
                <TableRow><TableCell colSpan={6} className="h-24 text-center">No clients found.</TableCell></TableRow>
              ) : filteredClients.map((client, index) => (
                <TableRow key={client.id} className="hover:bg-slate-50 border-b border-slate-200">
                  <TableCell className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                        <Building2 className="w-5 h-5 text-blue-600" />
                      </div>
                      <span className="font-medium text-slate-900">{client.name}</span>
                    </div>
                  </TableCell>
                  <TableCell className="px-4 py-3 text-center">
                    <span className={cn(
                      "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                      client.status === 'active' ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                    )}>
                      {client.status.charAt(0).toUpperCase() + client.status.slice(1)}
                    </span>
                  </TableCell>
                  <TableCell className="px-4 py-3 text-center"><CpmCell clientId={client.id} source="surfside" /></TableCell>
                  <TableCell className="px-4 py-3 text-center"><CpmCell clientId={client.id} source="facebook" /></TableCell>
                  <TableCell className="px-4 py-3 text-slate-600 text-sm">{new Date(client.createdAt).toLocaleDateString()}</TableCell>
                  <TableCell className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button variant="ghost" size="sm" onClick={() => handleSimulate(client)} className="gap-2"><Eye className="w-4 h-4" /> View</Button>
                      <Button variant="ghost" size="sm" onClick={() => { setEditingClient(client); setIsDialogOpen(true); }} className="gap-2"><Edit2 className="w-4 h-4" /> Edit</Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => { setClientToDelete(client); setIsDeleteDialogOpen(true); }}
                        className="gap-2 text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>

      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the client
              <strong> {clientToDelete?.name}</strong> and their associated user account.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              Delete Client
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

    </div>
  );
}
