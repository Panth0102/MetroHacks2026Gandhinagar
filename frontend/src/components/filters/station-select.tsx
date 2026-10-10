import { Label } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useStations } from "@/hooks/queries";

export function StationSelect({
  value,
  onChange,
  includeAll = true,
  label = "Station",
  id = "station-select",
}: {
  value: number | undefined;
  onChange: (id: number | undefined) => void;
  includeAll?: boolean;
  label?: string;
  id?: string;
}) {
  const { data } = useStations({ limit: 200 });
  const options = (data?.items ?? []).map((s) => ({
    value: String(s.id),
    label: `${s.name} (${s.code})`,
  }));
  return (
    <div>
      <Label htmlFor={id}>{label}</Label>
      <Select
        id={id}
        options={options}
        placeholder={includeAll ? "All stations" : undefined}
        value={value === undefined ? "" : String(value)}
        onChange={(e) => onChange(e.target.value === "" ? undefined : Number(e.target.value))}
      />
    </div>
  );
}
