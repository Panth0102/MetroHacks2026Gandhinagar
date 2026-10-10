import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "@/components/layout/app-shell";
import { InventoryPage } from "@/features/inventory/InventoryPage";
import { SpaceDetailPage } from "@/features/inventory/SpaceDetailPage";
import { OpportunitiesPage } from "@/features/opportunities/OpportunitiesPage";
import { OverviewPage } from "@/features/overview/OverviewPage";
import { PricingPage } from "@/features/pricing/PricingPage";
import { GenerateProposalPage } from "@/features/proposals/GenerateProposalPage";
import { ProposalEditorPage } from "@/features/proposals/ProposalEditorPage";
import { ProposalsListPage } from "@/features/proposals/ProposalsListPage";
import { ScenariosPage } from "@/features/scenarios/ScenariosPage";
import { StationsPage } from "@/features/stations/StationsPage";
import { NotFoundPage } from "@/features/NotFoundPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <OverviewPage /> },
      { path: "stations", element: <StationsPage /> },
      { path: "inventory", element: <InventoryPage /> },
      { path: "inventory/:id", element: <SpaceDetailPage /> },
      { path: "pricing", element: <PricingPage /> },
      { path: "opportunities", element: <OpportunitiesPage /> },
      { path: "scenarios", element: <ScenariosPage /> },
      { path: "proposals", element: <ProposalsListPage /> },
      { path: "proposals/new", element: <GenerateProposalPage /> },
      { path: "proposals/:id", element: <ProposalEditorPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
