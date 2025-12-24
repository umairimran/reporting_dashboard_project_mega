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
} from "@/components/ui/dialog";
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
import { Client, ClientSettings } from "@/types/dashboard";
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

const formSchema = z.object({
  name: z.string().min(2, "Client name must be at least 2 characters"),
  surfsideCpm: z.string().optional(),
  facebookCpm: z.string().optional(),
  // S3 Credentials
  s3BucketName: z.string().optional(),
  s3Region: z.string().optional(),
  s3AccessKeyId: z.string().optional(),
  s3SecretAccessKey: z.string().optional(),
});

// Component to fetch and display CPM for a client/source
const CpmCell = ({ clientId, source }: { clientId: string, source: "surfside" | "facebook" }) => {
  const { data: settings } = useQuery({
    queryKey: ["client-settings", clientId],
    queryFn: () => clientsService.getCpmSettings(clientId),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Find latest setting for source
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
  const [formTab, setFormTab] = useState<"basic" | "credentials">("basic");

  const { simulateAsClient, simulatedClient, isAdmin, user } = useAuth();
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
      surfsideCpm: "",
      facebookCpm: "",
      s3BucketName: "",
      s3Region: "us-east-1",
      s3AccessKeyId: "",
      s3SecretAccessKey: "",
    },
  });

  // Fetch settings when editing to pre-fill form
  // We use a query enabled only when editingClient is set
  const { data: editingSettings } = useQuery({
    queryKey: ["client-settings", editingClient?.id],
    queryFn: () => clientsService.getCpmSettings(editingClient!.id),
    enabled: !!editingClient,
  });

  // Reset form when opening dialog or switching clients
  useEffect(() => {
    if (isDialogOpen) {
      if (editingClient) {
        // Pre-fill form from editingClient + fetched settings
        const surfside = editingSettings?.find(s => s.source === "surfside")?.cpm;
        const facebook = editingSettings?.find(s => s.source === "facebook")?.cpm;

        form.reset({
          name: editingClient.name,
          surfsideCpm: surfside ? String(surfside) : "",
          facebookCpm: facebook ? String(facebook) : "",
          s3BucketName: "", // Todo: Fetch these
          s3Region: "us-east-1",
          s3AccessKeyId: "",
          s3SecretAccessKey: "",
        });
      } else {
        form.reset({
          name: "",
          surfsideCpm: "",
          facebookCpm: "",
          s3BucketName: "",
          s3Region: "us-east-1",
          s3AccessKeyId: "",
          s3SecretAccessKey: "",
        });
      }
    }
  }, [isDialogOpen, editingClient, editingSettings, form]);

  // Mutations
  const createClientMutation = useMutation({
    mutationFn: clientsService.createClient,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "clients"] });
      toast.success("Client created successfully");
      setIsDialogOpen(false);
      form.reset();
    },
    onError: (error) => {
      toast.error("Failed to create client");
      console.error(error);
    }
  });

  const updateClientMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => clientsService.updateClient(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "clients"] });
      toast.success("Client updated successfully");
      setIsDialogOpen(false);
      setEditingClient(null);
      form.reset();
    },
    onError: (error) => {
      toast.error("Failed to update client");
      console.error(error);
    }
  });

  const saveCpmMutation = useMutation({
    mutationFn: ({ clientId, source, cpm }: { clientId: string, source: "surfside" | "facebook", cpm: number }) =>
      clientsService.updateCpmSetting(clientId, { source, cpm }),
    onSuccess: (_, variables) => {
      // Invalidate specific client settings to refresh the table cell
      queryClient.invalidateQueries({ queryKey: ["client-settings", variables.clientId] });
    }
  });

  // Helper to sync multiple CPMs
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
        // Update
        await updateClientMutation.mutateAsync({ id: editingClient.id, data: { name: values.name } });
        await syncCpms(editingClient.id, values);
      } else {
        // Create
        // Use current admin user ID to satisfy FK constraint
        if (!user?.id) {
            toast.error("User context missing. Cannot create client.");
            // Generate a random UUID v4 placeholder as fallback if user.id is missing (should not happen for logged in admin)
            // But better to fail than create invalid data? 
            // The user requested: "if it is not available, update the backend function to use the client user."
            // But backend requires a valid UUID that exists in users table. So we must use a valid ID.
            return;
        }

        const newClient = await createClientMutation.mutateAsync({ name: values.name, user_id: user.id });
        if (newClient) {
          await syncCpms(newClient.id, values);
        }
      }
    } catch (error) {
      console.error("Error submitting form", error);
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
                // Form reset is handled by effect
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
            </DialogHeader>

            {/* Tabs */}
            <div className="flex items-center gap-2 p-1 bg-slate-100 rounded-xl mb-4 w-fit">
              <button
                type="button"
                onClick={() => setFormTab("basic")}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  formTab === "basic"
                    ? "bg-blue-500 text-white shadow-lg"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
                )}
              >
                Basic Info
              </button>
              <button
                type="button"
                onClick={() => setFormTab("credentials")}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  formTab === "credentials"
                    ? "bg-blue-500 text-white shadow-lg"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
                )}
              >
                Credentials
              </button>
            </div>

            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-4"
              >
                {/* Basic Info Tab */}
                {formTab === "basic" && (
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>
                            Client Name <span className="text-red-500">*</span>
                          </FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Acme Corp"
                              className="bg-white"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="border-t border-slate-200 pt-4 mt-4">
                      <h3 className="text-sm font-semibold text-slate-900 mb-4">
                        Update CPM Settings (Optional)
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <FormField
                          control={form.control}
                          name="surfsideCpm"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Surfside CPM</FormLabel>
                              <FormControl>
                                <div className="relative">
                                  <DollarSign className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
                                  <Input
                                    type="number"
                                    step="0.01"
                                    placeholder="0.00"
                                    className="pl-9 bg-white"
                                    {...field}
                                  />
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
                                  <Input
                                    type="number"
                                    step="0.01"
                                    placeholder="0.00"
                                    className="pl-9 bg-white"
                                    {...field}
                                  />
                                </div>
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Credentials Tab */}
                {formTab === "credentials" && (
                  <div className="space-y-6">
                    <div>
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
                          <Cloud className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <h3 className="text-sm font-semibold text-slate-900">
                            S3 Configuration (Optional)
                          </h3>
                          <p className="text-xs text-slate-600">
                            For Surfside data sync
                          </p>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <FormField
                          control={form.control}
                          name="s3BucketName"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Bucket Name</FormLabel>
                              <FormControl>
                                <Input
                                  placeholder="my-analytics-bucket"
                                  className="bg-white"
                                  {...field}
                                />
                              </FormControl>
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
                                <select
                                  {...field}
                                  className="w-full h-10 px-4 rounded-lg border border-slate-200 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                                >
                                  <option value="us-east-1">
                                    US East (N. Virginia)
                                  </option>
                                  <option value="us-west-2">
                                    US West (Oregon)
                                  </option>
                                  <option value="eu-west-1">
                                    EU (Ireland)
                                  </option>
                                  <option value="ap-south-1">
                                    Asia Pacific (Mumbai)
                                  </option>
                                  <option value="ap-southeast-1">
                                    Asia Pacific (Singapore)
                                  </option>
                                </select>
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={form.control}
                          name="s3AccessKeyId"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Access Key ID</FormLabel>
                              <FormControl>
                                <Input
                                  type="password"
                                  placeholder="Enter Access Key ID"
                                  className="bg-white"
                                  {...field}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        <FormField
                          control={form.control}
                          name="s3SecretAccessKey"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Secret Access Key</FormLabel>
                              <FormControl>
                                <Input
                                  type="password"
                                  placeholder="Enter Secret Access Key"
                                  className="bg-white"
                                  {...field}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-slate-200">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => setIsDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" variant="gold" disabled={createClientMutation.isPending || updateClientMutation.isPending}>
                    {createClientMutation.isPending || updateClientMutation.isPending ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : null}
                    {editingClient ? "Save Changes" : "Add Client"}
                  </Button>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600" />
          <Input
            placeholder="Search clients..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Clients Table */}
      <div className="bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Loading clients...</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent border-b border-slate-200">
                <TableHead className="text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto">
                  Client
                </TableHead>
                <TableHead className="text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto">
                  Status
                </TableHead>
                <TableHead className="text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto text-center">
                  CPM - Surfside
                </TableHead>
                <TableHead className="text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto text-center">
                  CPM - Facebook
                </TableHead>
                <TableHead className="text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto">
                  Created
                </TableHead>
                <TableHead className="text-right text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto">
                  Actions
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredClients.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-24 text-center">
                    No clients found.
                  </TableCell>
                </TableRow>
              ) : filteredClients.map((client, index) => {
                return (
                  <TableRow
                    key={client.id}
                    className="opacity-0 animate-[fadeIn_0.5s_ease-out_forwards] border-b border-slate-200 hover:bg-slate-100/50 transition-colors"
                    style={{ animationDelay: `${index * 30}ms` }}
                  >
                    <TableCell className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                          <Building2 className="w-5 h-5 text-blue-600" />
                        </div>
                        <span className="font-medium text-slate-900">
                          {client.name}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="px-4 py-3">
                      <span
                        className={cn(
                          "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize",
                          client.status === "active"
                            ? "bg-green-500/20 text-green-600"
                            : "bg-gray-500/20 text-gray-600"
                        )}
                      >
                        {client.status}
                      </span>
                    </TableCell>
                    <TableCell className="font-mono text-sm px-4 py-3 text-center">
                      <CpmCell clientId={client.id} source="surfside" />
                    </TableCell>
                    <TableCell className="font-mono text-sm px-4 py-3 text-center">
                      <CpmCell clientId={client.id} source="facebook" />
                    </TableCell>
                    <TableCell className="text-slate-600 text-sm px-4 py-3">
                      {new Date(client.createdAt).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleSimulate(client)}
                          className="gap-2 cursor-pointer hover:bg-gray-200"
                        >
                          <Eye className="w-4 h-4" />
                          View
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setEditingClient(client);
                            setIsDialogOpen(true);
                          }}
                          className="gap-2 cursor-pointer hover:bg-gray-200"
                        >
                          <Edit2 className="w-4 h-4" />
                          Edit
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
