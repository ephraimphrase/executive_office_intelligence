import React from "react";
import CommunicationsClient from "./CommunicationsClient";
import { fetchEmails } from "@/lib/api";
import { getServerCookieHeader } from "@/lib/server-cookies";

export default async function CommunicationsPage() {
  const cookieHeader = await getServerCookieHeader();
  const emails = await fetchEmails(cookieHeader);

  return <CommunicationsClient emails={emails} />;
}
