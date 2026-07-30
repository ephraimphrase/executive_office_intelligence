"use client";

import React from "react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import KanbanBoard from "@/components/tasks/KanbanBoard";
import { Task } from "@/lib/api";

interface TasksClientProps {
  tasks: Task[];
}

export default function TasksClient({ tasks }: TasksClientProps) {
  return (
    <>
      <Sidebar />
      <TopNav title="Task Intelligence" />
      <main className="md:ml-64 pt-20 p-12 min-h-[calc(100vh-80px)] max-w-[1440px] mx-auto">
        <KanbanBoard tasks={tasks} />
      </main>
    </>
  );
}
