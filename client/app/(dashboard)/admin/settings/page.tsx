"use client";

import { useState } from "react";
import { Save, Bell, Shield, Clock, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";

export default function AdminSettings() {
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [autoSync, setAutoSync] = useState(true);
  const [syncFrequency, setSyncFrequency] = useState("daily");
  const [retryFailed, setRetryFailed] = useState(true);
  const [notifyFailures, setNotifyFailures] = useState(true);
  const [notifyReports, setNotifyReports] = useState(true);
  const [sessionTimeout, setSessionTimeout] = useState("60");
  const [auditLogging, setAuditLogging] = useState(true);

  const handleChange = () => {
    setHasUnsavedChanges(true);
  };

  const handleSave = () => {
    setHasUnsavedChanges(false);
    alert("Settings saved successfully!");
  };

  return (
    <div className="p-8 flex justify-center">
      <div className="w-full max-w-3xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
              <p className="text-slate-600">
                Configure system-wide settings and preferences
              </p>
            </div>
            {hasUnsavedChanges && (
              <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 border border-amber-200 rounded-lg">
                <AlertCircle className="w-4 h-4 text-amber-600" />
                <span className="text-sm font-medium text-amber-900">
                  Unsaved changes
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Settings Sections */}
        <div className="space-y-6">
          {/* Data Sync Settings */}
          <div className="bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Clock className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Data Sync Schedule
                </h2>
                <p className="text-sm text-slate-600">
                  Configure automatic data ingestion
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between py-3 ">
                <div>
                  <p className="font-medium text-slate-900">
                    Enable Automatic Sync
                  </p>
                  <p className="text-sm text-slate-600">
                    Automatically sync data from Vibe and Surfside using API and
                    S3 bucket
                  </p>
                </div>
                <Switch
                  checked={autoSync}
                  onCheckedChange={(checked) => {
                    setAutoSync(checked);
                    handleChange();
                  }}
                />
              </div>

              {/* <div className="flex items-center justify-between py-3 border-b border-slate-200">
                <div>
                  <p className="font-medium text-slate-900">Sync Frequency</p>
                  <p className="text-sm text-slate-600">
                    How often to pull new data
                  </p>
                </div>
                <select
                  value={syncFrequency}
                  onChange={(e) => {
                    setSyncFrequency(e.target.value);
                    handleChange();
                  }}
                  className="h-9 px-3 rounded-lg border border-slate-200 bg-white text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/30 cursor-pointer"
                >
                  <option value="hourly">Every Hour</option>
                  <option value="daily">Daily (6 AM)</option>
                  <option value="manual">Manual Only</option>
                </select>
              </div> */}

              {/* <div className="flex items-center justify-between py-3">
                <div>
                  <p className="font-medium text-slate-900">
                    Retry Failed Jobs
                  </p>
                  <p className="text-sm text-slate-600">
                    Automatically retry failed ingestions
                  </p>
                </div>
                <Switch
                  checked={retryFailed}
                  onCheckedChange={(checked) => {
                    setRetryFailed(checked);
                    handleChange();
                  }}
                />
              </div> */}
            </div>
          </div>

          {/* Notification Settings */}
          <div
            className="bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]"
            style={{ animationDelay: "100ms" }}
          >
            <div className="flex items-center gap-4 mb-6">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Bell className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Notifications
                </h2>
                <p className="text-sm text-slate-600">
                  Manage alert preferences
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b border-slate-200">
                <div>
                  <p className="font-medium text-slate-900">
                    Ingestion Failures
                  </p>
                  <p className="text-sm text-slate-600">
                    Get notified when data sync fails
                  </p>
                </div>
                <Switch
                  checked={notifyFailures}
                  onCheckedChange={(checked) => {
                    setNotifyFailures(checked);
                    handleChange();
                  }}
                />
              </div>

              <div className="flex items-center justify-between py-3">
                <div>
                  <p className="font-medium text-slate-900">
                    Weekly Report Ready
                  </p>
                  <p className="text-sm text-slate-600">
                    Notification when reports are generated
                  </p>
                </div>
                <Switch
                  checked={notifyReports}
                  onCheckedChange={(checked) => {
                    setNotifyReports(checked);
                    handleChange();
                  }}
                />
              </div>
            </div>
          </div>

          {/* Security Settings */}
          <div
            className="bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]"
            style={{ animationDelay: "200ms" }}
          >
            <div className="flex items-center gap-4 mb-6">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Shield className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Security
                </h2>
                <p className="text-sm text-slate-600">
                  Security and access settings
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b border-slate-200">
                <div>
                  <p className="font-medium text-slate-900">Session Timeout</p>
                  <p className="text-sm text-slate-600">
                    Auto-logout after inactivity
                  </p>
                </div>
                <select
                  value={sessionTimeout}
                  onChange={(e) => {
                    setSessionTimeout(e.target.value);
                    handleChange();
                  }}
                  className="h-9 px-3 rounded-lg border border-slate-200 bg-white text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/30 cursor-pointer"
                >
                  <option value="30">30 minutes</option>
                  <option value="60">1 hour</option>
                  <option value="240">4 hours</option>
                </select>
              </div>

              <div className="flex items-center justify-between py-3">
                <div>
                  <p className="font-medium text-slate-900">Audit Logging</p>
                  <p className="text-sm text-slate-600">
                    Log all user actions for compliance
                  </p>
                </div>
                <Switch
                  checked={auditLogging}
                  onCheckedChange={(checked) => {
                    setAuditLogging(checked);
                    handleChange();
                  }}
                />
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button
              variant="gold"
              className="gap-2"
              onClick={handleSave}
              disabled={!hasUnsavedChanges}
            >
              <Save className="w-4 h-4" />
              Save Changes
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
