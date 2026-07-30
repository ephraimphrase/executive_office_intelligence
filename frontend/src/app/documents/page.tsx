import React from "react";
import DocumentsClient from "./DocumentsClient";
import { fetchDocuments } from "@/lib/api";
import { getServerCookieHeader } from "@/lib/server-cookies";

export default async function DocumentsPage() {
  const cookieHeader = await getServerCookieHeader();
  const documents = await fetchDocuments(cookieHeader);

  return <DocumentsClient documents={documents} />;
}
