import { cn } from '@/lib/utils';
import { DataSource } from '@/types/dashboard';

interface PlatformTabsProps {
  activeSource: DataSource | 'all';
  onChange: (source: DataSource | 'all') => void;
}

const platforms: { id: DataSource | 'all'; label: string; color: string }[] = [
  { id: 'all', label: 'All Platforms', color: '#f59e0b' },
  { id: 'surfside', label: 'Surfside', color: '#22c55e' },
  { id: 'facebook', label: 'Facebook', color: '#3b82f6' },
  { id: 'vibe', label: 'Vibe', color: '#a855f7' },
];

export default function PlatformTabs({ activeSource, onChange }: PlatformTabsProps) {
  return (
    <div className="flex items-center gap-2 p-1 bg-gray-100 rounded-xl">
      {platforms.map((platform) => (
        <button
          key={platform.id}
          onClick={() => onChange(platform.id)}
          className={cn(
            'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
            activeSource === platform.id
              ? 'text-white shadow-lg'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200'
          )}
          style={activeSource === platform.id ? {
            backgroundColor: platform.color,
            boxShadow: `0 10px 15px -3px ${platform.color}40, 0 4px 6px -4px ${platform.color}40, 0 0 20px ${platform.color}40`
          } : {}}
        >
          {platform.label}
        </button>
      ))}
    </div>
  );
}
