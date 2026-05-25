import { PageHeader } from "@/components/page-header";
import { KnowledgeBaseAdmin } from "@/components/knowledge-base-admin";

export default function UploadPage() {
  return (
    <>
      <PageHeader eyebrow="Curriculum ingestion" title="Knowledge base manager" />
      <KnowledgeBaseAdmin />
    </>
  );
}
