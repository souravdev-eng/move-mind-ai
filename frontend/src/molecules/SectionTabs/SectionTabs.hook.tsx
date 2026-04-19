import { useLocation, useNavigate } from "react-router-dom";

import { type TabItem } from "./SectionTabs";

export function useSectionTabs(tabs: TabItem[]) {
  const nav = useNavigate();
  const { pathname } = useLocation();
  const activeIdx = Math.max(
    0,
    tabs.findIndex((t) =>
      t.match ? t.match(pathname) : pathname === t.to || pathname.startsWith(`${t.to}/`),
    ),
  );
  function navigate(newIdx: number) {
    const t = tabs[newIdx];
    if (t) {
      nav(t.to);
    }
  }
  return { activeIdx, navigate };
}
