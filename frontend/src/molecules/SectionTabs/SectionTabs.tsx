import { Tab, Tabs } from "@mui/material";

import { useSectionTabs } from "./SectionTabs.hook";

export interface TabItem {
  label: string;
  to: string;
  match?: (pathname: string) => boolean;
}

export function SectionTabs({ tabs }: { tabs: TabItem[] }) {
  const { activeIdx, navigate } = useSectionTabs(tabs);
  return (
    <Tabs
      value={activeIdx}
      onChange={(_e, newIdx: number) => {
        navigate(newIdx);
      }}
      sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}
    >
      {tabs.map((t) => (
        <Tab key={t.to} label={t.label} />
      ))}
    </Tabs>
  );
}
