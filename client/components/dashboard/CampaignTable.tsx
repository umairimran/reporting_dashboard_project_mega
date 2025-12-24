import { CampaignPerformance, DataSource } from "@/types/dashboard";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

interface CampaignTableProps {
  campaigns: CampaignPerformance[];
}

const sourceColors: Record<DataSource, string> = {
  surfside: "bg-green-500/20 text-green-400",
  facebook: "bg-blue-500/20 text-blue-400",
  vibe: "bg-purple-500/20 text-purple-400",
};

export default function CampaignTable({ campaigns }: CampaignTableProps) {
  if (campaigns.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="w-16 h-16 mb-4 rounded-full bg-slate-100 flex items-center justify-center">
          <svg
            className="w-8 h-8 text-slate-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <p className="text-lg font-medium text-slate-900 mb-2">
          No Campaigns Available
        </p>
        <p className="text-sm text-slate-600">
          There are no campaigns to display at this time.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      \n{" "}
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="text-left text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 border-b border-slate-200">
              Campaign
            </th>
            <th className="text-left text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 border-b border-slate-200">
              Platform
            </th>
            <th className="text-right text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 border-b border-slate-200">
              Impressions
            </th>
            <th className="text-right text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 border-b border-slate-200">
              Clicks
            </th>
            <th className="text-right text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 border-b border-slate-200">
              CTR
            </th>
            <th className="text-right text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 border-b border-slate-200">
              Spend
            </th>
            <th className="text-right text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 border-b border-slate-200">
              Revenue
            </th>
            <th className="text-right text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 border-b border-slate-200">
              ROAS
            </th>
          </tr>
        </thead>
        <tbody>
          \n{" "}
          {campaigns.map((campaign, index) => (
            <tr
              key={campaign.campaignId}
              className="opacity-0 animate-[fadeIn_0.5s_ease-out_forwards] border-b border-slate-200 hover:bg-slate-50 transition-colors"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <td className="px-4 py-3">
                <span className="font-medium text-slate-900">
                  {campaign.campaignName}
                </span>
              </td>
              <td className="px-4 py-3">
                <span
                  className={cn(
                    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize",
                    sourceColors[campaign.source]
                  )}
                >
                  {campaign.source}
                </span>
              </td>
              <td className="text-right font-mono text-sm px-4 py-3 text-slate-900">
                {formatNumber(campaign.impressions)}
              </td>
              <td className="text-right font-mono text-sm">
                {formatNumber(campaign.clicks)}
              </td>
              <td className="text-right font-mono text-sm">
                {formatPercent(campaign.ctr)}
              </td>
              <td className="text-right font-mono text-sm">
                {formatCurrency(campaign.spend)}
              </td>
              <td className="text-right font-mono text-sm px-4 py-3 text-amber-600">
                {formatCurrency(campaign.revenue)}
              </td>
              <td className="text-right">
                <span
                  className={cn(
                    "font-mono text-sm font-semibold",
                    campaign.roas >= 3
                      ? "text-green-400"
                      : campaign.roas >= 2
                      ? "text-amber-600"
                      : "text-red-400"
                  )}
                >
                  {campaign.roas.toFixed(2)}x
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
