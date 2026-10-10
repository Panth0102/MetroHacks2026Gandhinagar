import { Download, FileText } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { statusLabel, statusTone } from "@/components/proposals/ProposalPreview";
import { QueryState } from "@/components/feedback/state";
import { PageIntro } from "@/components/layout/page";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Pagination } from "@/components/ui/pagination";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { api } from "@/lib/api-client";
import { formatDate } from "@/lib/formatters";
import { useProposals } from "@/hooks/queries";

const PAGE_SIZE = 15;

export function ProposalsListPage() {
  const [offset, setOffset] = useState(0);
  const query = useProposals({ limit: PAGE_SIZE, offset });

  return (
    <div>
      <PageIntro
        title="Sales proposals"
        description="One-page proposals generated from verified backend data. Open a proposal to edit, regenerate, or download its PDF."
      />
      <QueryState
        query={query}
        isEmpty={(p) => p.total === 0}
        emptyTitle="No proposals yet"
        emptyHint="Open a vacant space in Commercial Inventory and choose “Generate sales proposal”."
      >
        {(page) => (
          <Card>
            <CardContent className="p-0">
              <Table>
                <THead>
                  <TR>
                    <TH>Reference</TH>
                    <TH>Title</TH>
                    <TH>Category</TH>
                    <TH>Source</TH>
                    <TH>Status</TH>
                    <TH>Updated</TH>
                    <TH className="sr-only">Actions</TH>
                  </TR>
                </THead>
                <TBody>
                  {page.items.map((p) => (
                    <TR key={p.id}>
                      <TD className="font-medium">{p.reference_code}</TD>
                      <TD className="max-w-xs truncate">{p.title}</TD>
                      <TD>{p.tenant_category ?? "—"}</TD>
                      <TD>
                        <Badge tone={p.generation_source === "ai" ? "accent" : "neutral"}>
                          {p.generation_source === "ai" ? "AI" : "Template"}
                        </Badge>
                      </TD>
                      <TD>
                        <Badge tone={statusTone(p.status)}>{statusLabel(p.status)}</Badge>
                      </TD>
                      <TD>{formatDate(p.updated_at)}</TD>
                      <TD className="text-right">
                        <div className="flex justify-end gap-3">
                          <Link
                            to={`/proposals/${p.id}`}
                            className="inline-flex items-center gap-1 text-sm font-medium text-accent hover:underline"
                          >
                            <FileText className="h-4 w-4" /> Open
                          </Link>
                          <a
                            href={api.downloadUrl(`/api/v1/proposals/${p.id}/pdf`)}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 text-sm font-medium text-accent hover:underline"
                          >
                            <Download className="h-4 w-4" /> PDF
                          </a>
                        </div>
                      </TD>
                    </TR>
                  ))}
                </TBody>
              </Table>
              <div className="px-4 pb-3">
                <Pagination offset={offset} limit={PAGE_SIZE} total={page.total} onChange={setOffset} />
              </div>
            </CardContent>
          </Card>
        )}
      </QueryState>
    </div>
  );
}
