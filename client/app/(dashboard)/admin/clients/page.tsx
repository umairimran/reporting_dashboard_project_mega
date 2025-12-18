"use client";

import { useState, useEffect } from "react";
import {
  Search,
  Plus,
  Edit2,
  Eye,
  MoreHorizontal,
  Building2,
  Settings,
  DollarSign,
  Cloud,
  MonitorPlay,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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
import { mockClients, mockClientSettings } from "@/lib/mock-data";
import { ClientSettings, Client } from "@/types/dashboard";
import { cn } from "@/lib/utils";

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
  vibeCpm: z.string().optional(),
  facebookCpm: z.string().optional(),
  // S3 Credentials
  s3BucketName: z.string().optional(),
  s3Region: z.string().optional(),
  s3AccessKeyId: z.string().optional(),
  s3SecretAccessKey: z.string().optional(),
  // Vibe Credentials
  vibeApiKey: z.string().optional(),
  vibeAdvertiserId: z.string().optional(),
});

export default function AdminClients() {
  const [clients, setClients] = useState(mockClients);
  const [clientSettings, setClientSettings] = useState(mockClientSettings);
  const [searchQuery, setSearchQuery] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [formTab, setFormTab] = useState<"basic" | "credentials">("basic");

  const { simulateAsClient, simulatedClient, isAdmin } = useAuth();
  const router = useRouter();

  // Redirect if viewing as client
  useEffect(() => {
    if (simulatedClient && isAdmin) {
      router.push("/dashboard");
    }
  }, [simulatedClient, isAdmin, router]);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      surfsideCpm: "",
      vibeCpm: "",
      facebookCpm: "",
      s3BucketName: "",
      s3Region: "us-east-1",
      s3AccessKeyId: "",
      s3SecretAccessKey: "",
      vibeApiKey: "",
      vibeAdvertiserId: "",
    },
  });

  useEffect(() => {
    if (isDialogOpen) {
      if (editingClient) {
        const settings = getClientSettings(editingClient.id);
        const surfside =
          settings.find((s) => s.source === "surfside")?.cpm?.toString() || "";
        const vibe =
          settings.find((s) => s.source === "vibe")?.cpm?.toString() || "";
        const facebook =
          settings.find((s) => s.source === "facebook")?.cpm?.toString() || "";

        // TODO: Load S3 and Vibe credentials from storage
        form.reset({
          name: editingClient.name,
          surfsideCpm: surfside,
          vibeCpm: vibe,
          facebookCpm: facebook,
          s3BucketName: "",
          s3Region: "us-east-1",
          s3AccessKeyId: "",
          s3SecretAccessKey: "",
          vibeApiKey: "",
          vibeAdvertiserId: "",
        });
      } else {
        form.reset({
          name: "",
          surfsideCpm: "",
          vibeCpm: "",
          facebookCpm: "",
          s3BucketName: "",
          s3Region: "us-east-1",
          s3AccessKeyId: "",
          s3SecretAccessKey: "",
          vibeApiKey: "",
          vibeAdvertiserId: "",
        });
      }
      setFormTab("basic");
    }
  }, [
    isDialogOpen,
    editingClient /* clientSettings is stable enough or we ignore it to avoid loop */,
  ]);

  const filteredClients = clients.filter((client) =>
    client.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSimulate = (client: (typeof mockClients)[0]) => {
    simulateAsClient(client);
    router.push("/dashboard");
  };

  const getClientSettings = (clientId: string) => {
    return clientSettings.filter((s) => s.clientId === clientId);
  };

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    if (editingClient) {
      // Update existing client
      setClients((prev) =>
        prev.map((c) =>
          c.id === editingClient.id ? { ...c, name: values.name } : c
        )
      );

      // Update settings
      setClientSettings((prev) => {
        // Remove old settings for this client
        const filtered = prev.filter((s) => s.clientId !== editingClient.id);
        const newSettings: ClientSettings[] = [];

        if (values.surfsideCpm) {
          newSettings.push({
            id: Math.random().toString(36).substr(2, 9),
            clientId: editingClient.id,
            source: "surfside" as const,
            cpm: parseFloat(values.surfsideCpm),
            currency: "USD",
          });
        }
        if (values.vibeCpm) {
          newSettings.push({
            id: Math.random().toString(36).substr(2, 9),
            clientId: editingClient.id,
            source: "vibe" as const,
            cpm: parseFloat(values.vibeCpm),
            currency: "USD",
          });
        }
        if (values.facebookCpm) {
          newSettings.push({
            id: Math.random().toString(36).substr(2, 9),
            clientId: editingClient.id,
            source: "facebook" as const,
            cpm: parseFloat(values.facebookCpm),
            currency: "USD",
          });
        }
        return [...filtered, ...newSettings];
      });
    } else {
      // Create new client
      const newClientId = Math.random().toString(36).substr(2, 9);

      // Add new client
      const newClient = {
        id: newClientId,
        name: values.name,
        status: "active" as const,
        userId: "new-user", // In a real app this would be linked to a user
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      setClients((prev) => [newClient, ...prev]);

      // Add settings if CPMs are provided
      const newSettings: ClientSettings[] = [];
      if (values.surfsideCpm) {
        newSettings.push({
          id: Math.random().toString(36).substr(2, 9),
          clientId: newClientId,
          source: "surfside" as const,
          cpm: parseFloat(values.surfsideCpm),
          currency: "USD",
        });
      }
      if (values.vibeCpm) {
        newSettings.push({
          id: Math.random().toString(36).substr(2, 9),
          clientId: newClientId,
          source: "vibe" as const,
          cpm: parseFloat(values.vibeCpm),
          currency: "USD",
        });
      }
      if (values.facebookCpm) {
        newSettings.push({
          id: Math.random().toString(36).substr(2, 9),
          clientId: newClientId,
          source: "facebook" as const,
          cpm: parseFloat(values.facebookCpm),
          currency: "USD",
        });
      }

      if (newSettings.length > 0) {
        setClientSettings((prev) => [...prev, ...newSettings]);
      }
    }

    setIsDialogOpen(false);
    form.reset();
    setEditingClient(null);
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
            Manage client accounts and CPM configurations
          </p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button
              variant="gold"
              className="gap-2"
              onClick={() => setEditingClient(null)}
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
                        CPM Settings (Optional)
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                          name="vibeCpm"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Vibe CPM</FormLabel>
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
                    {/* S3 Credentials Section */}
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

                    {/* Vibe Credentials Section */}
                    <div className="border-t border-slate-200 pt-6">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
                          <MonitorPlay className="w-5 h-5 text-purple-600" />
                        </div>
                        <div>
                          <h3 className="text-sm font-semibold text-slate-900">
                            Vibe Configuration (Optional)
                          </h3>
                          <p className="text-xs text-slate-600">
                            For Vibe campaign sync
                          </p>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <FormField
                          control={form.control}
                          name="vibeApiKey"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>API Key</FormLabel>
                              <FormControl>
                                <Input
                                  type="password"
                                  placeholder="Enter Vibe API Key"
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
                          name="vibeAdvertiserId"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Advertiser ID</FormLabel>
                              <FormControl>
                                <Input
                                  placeholder="Enter Advertiser ID"
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
                  <Button type="submit" variant="gold">
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
                CPM - Vibe
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
            {filteredClients.map((client, index) => {
              const settings = getClientSettings(client.id);
              const surfsideCpm = settings.find(
                (s) => s.source === "surfside"
              )?.cpm;
              const vibeCpm = settings.find((s) => s.source === "vibe")?.cpm;
              const facebookCpm = settings.find(
                (s) => s.source === "facebook"
              )?.cpm;

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
                    {surfsideCpm ? `$${surfsideCpm.toFixed(2)}` : "—"}
                  </TableCell>
                  <TableCell className="font-mono text-sm px-4 py-3 text-center">
                    {vibeCpm ? `$${vibeCpm.toFixed(2)}` : "—"}
                  </TableCell>
                  <TableCell className="font-mono text-sm px-4 py-3 text-center">
                    {facebookCpm ? `$${facebookCpm.toFixed(2)}` : "—"}
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
                        className="gap-2"
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
                        className="gap-2"
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
      </div>
    </div>
  );
}
