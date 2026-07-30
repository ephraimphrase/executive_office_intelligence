import React from "react";
import TasksClient from "./TasksClient";
import { fetchTasks } from "@/lib/api";
import { getServerCookieHeader } from "@/lib/server-cookies";

export default async function TasksPage() {
  const cookieHeader = await getServerCookieHeader();
  const tasks = await fetchTasks(cookieHeader);

  return <TasksClient tasks={tasks} />;
}
