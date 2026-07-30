"use client";

import React, { useState } from "react";
import { Task, createTask } from "@/lib/api";

interface KanbanBoardProps {
  tasks: Task[];
}

export default function KanbanBoard({ tasks: initialTasks }: KanbanBoardProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [filter, setFilter] = useState("All");
  const [isCreating, setIsCreating] = useState(false);

  const pendingReview = tasks.filter((t) => t.status === "TODO");
  const waiting = tasks.filter((t) => t.status === "WAITING");
  const inProgress = tasks.filter((t) => t.status === "IN_PROGRESS");
  const completed = tasks.filter((t) => t.status === "DONE");

  // In the real app, we would also filter by department based on `filter` state
  // and handle the task card rendering based on priority, etc.

  const handleCreateTask = async () => {
    const title = prompt("Enter task title:");
    if (!title) return;

    try {
      setIsCreating(true);
      const newTask = await createTask({
        title,
        description: "",
        due_date: new Date(Date.now() + 86400000).toISOString(),
        priority: "MEDIUM",
        status: "TODO",
        department: filter === "All" ? null : filter,
      });
      setTasks(prev => [...prev, newTask]);
    } catch {
      alert("Failed to create task");
    } finally {
      setIsCreating(false);
    }
  };

  const renderTaskCard = (task: Task, columnType: "TODO" | "WAITING" | "IN_PROGRESS" | "DONE") => {
    // Determine priority color based on column and priority
    let priorityBg = "bg-secondary/10";
    let priorityText = "text-secondary";
    if (task.priority === "CRITICAL") {
      priorityBg = "bg-error/10";
      priorityText = "text-error";
    } else if (task.priority === "HIGH") {
      priorityBg = "bg-error/10"; // Using same as critical for now based on mockup
      priorityText = "text-error";
    } else if (task.priority === "MEDIUM") {
      priorityBg = "bg-amber-100";
      priorityText = "text-amber-700";
    }

    if (columnType === "DONE") {
      return (
        <div key={task.id} className="glass-card p-5 rounded-lg flex flex-col gap-4 group transition-all grayscale-[0.5]">
          <div className="flex justify-between items-start">
            <span className="px-2 py-1 rounded bg-surface-container-highest text-on-surface-variant text-[10px] font-bold uppercase tracking-tighter line-through">
              Complete
            </span>
            <span className="material-symbols-outlined text-green-600 text-[18px]">check_circle</span>
          </div>
          <h4 className="font-label-md text-on-surface leading-snug line-through">{task.title}</h4>
          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-slate-200 border border-white flex items-center justify-center overflow-hidden">
                <span className="material-symbols-outlined text-[14px] text-slate-500">person</span>
              </div>
              <span className="text-label-sm text-on-surface-variant">
                Finished {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'Recently'}
              </span>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div key={task.id} className="glass-card p-5 rounded-lg flex flex-col gap-4 group cursor-pointer hover:border-primary/20 transition-all duration-300 hover:-translate-y-[2px]">
        <div className="flex justify-between items-start">
          <span className={`px-2 py-1 rounded ${priorityBg} ${priorityText} text-[10px] font-bold uppercase tracking-tighter`}>
            {task.priority}
          </span>
          <span className="material-symbols-outlined text-on-surface-variant text-[16px] opacity-0 group-hover:opacity-100 transition-opacity">open_in_new</span>
        </div>
        <h4 className="font-label-md text-on-surface leading-snug group-hover:text-primary transition-colors">{task.title}</h4>
        
        {columnType === "WAITING" && task.description && (
          <p className="text-[11px] text-on-surface-variant italic">{task.description}</p>
        )}

        {columnType === "IN_PROGRESS" && (
          <div className="w-full bg-surface-container h-1 rounded-full overflow-hidden mt-1">
            <div className="bg-primary h-full w-2/3"></div>
          </div>
        )}

        <div className="flex items-center justify-between mt-2">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-slate-200 border border-white flex items-center justify-center overflow-hidden">
              <span className="material-symbols-outlined text-[14px] text-slate-500">person</span>
            </div>
            <span className="text-label-sm text-on-surface-variant">
              Due {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'TBD'}
            </span>
          </div>
          {columnType === "TODO" && <span className="material-symbols-outlined text-on-surface-variant text-[18px]">attach_file</span>}
          {columnType === "IN_PROGRESS" && <span className="material-symbols-outlined text-primary text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>chat_bubble</span>}
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-6">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-primary mb-2">Task Intelligence</h2>
          <p className="text-on-surface-variant font-body-md">
            Real-time oversight of strategic operational priorities across global departments.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg border border-outline-variant/30 text-label-md hover:bg-slate-50 transition-colors">
            <span className="material-symbols-outlined text-[18px]">download</span>
            Export PDF
          </button>
          <button 
            onClick={handleCreateTask}
            disabled={isCreating}
            className="flex items-center gap-2 bg-primary text-on-primary px-6 py-2 rounded-lg text-label-md shadow-sm hover:opacity-90 active:scale-95 transition-all"
          >
            <span className="material-symbols-outlined text-[18px]">{isCreating ? "hourglass_empty" : "add"}</span>
            New Task
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-card rounded-xl p-4 mb-8 flex flex-col md:flex-row items-center gap-6">
        <div className="flex flex-wrap gap-2 items-center border-r border-outline-variant/30 pr-6">
          <span className="text-label-sm text-on-surface-variant mr-2 uppercase tracking-widest">Departments</span>
          {["All", "Legal", "Finance", "Operations", "Sales"].map((dept) => (
            <button
              key={dept}
              onClick={() => setFilter(dept)}
              className={`px-4 py-1.5 rounded-full text-label-md transition-all ${
                filter === dept ? "active-filter" : "text-on-surface-variant hover:bg-surface-container"
              }`}
            >
              {dept}
            </button>
          ))}
        </div>
        <div className="relative flex-grow">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">
            filter_list
          </span>
          <input
            id="task-search"
            type="text"
            placeholder="Search tasks by title, owner, or project..."
            className="w-full bg-transparent border-none text-label-md focus:ring-0 pl-10"
            onFocus={(e) => e.target.parentElement?.parentElement?.classList.add("ring-1", "ring-primary/20")}
            onBlur={(e) => e.target.parentElement?.parentElement?.classList.remove("ring-1", "ring-primary/20")}
          />
        </div>
        <div className="flex items-center gap-4 pl-4 border-l border-outline-variant/30">
          <button className="p-2 text-on-surface-variant hover:text-primary">
            <span className="material-symbols-outlined">grid_view</span>
          </button>
          <button className="p-2 text-primary bg-secondary-container rounded-lg">
            <span className="material-symbols-outlined">view_column</span>
          </button>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-gutter overflow-x-auto pb-4 custom-scrollbar">
        {/* Column: Pending Review */}
        <div className="flex flex-col gap-4 min-w-[280px]">
          <div className="flex items-center justify-between px-2">
            <div className="flex items-center gap-2">
              <h3 className="font-label-md text-label-md text-on-surface font-bold uppercase tracking-wider">Pending Review</h3>
              <span className="bg-surface-container-highest px-2 py-0.5 rounded text-[11px] font-bold">{pendingReview.length}</span>
            </div>
            <button className="text-on-surface-variant hover:text-primary"><span className="material-symbols-outlined text-[18px]">more_horiz</span></button>
          </div>
          <div className="kanban-column p-2 rounded-xl flex flex-col gap-4">
            {pendingReview.map(t => renderTaskCard(t, "TODO"))}
          </div>
        </div>

        {/* Column: Waiting on Others */}
        <div className="flex flex-col gap-4 min-w-[280px]">
          <div className="flex items-center justify-between px-2">
            <div className="flex items-center gap-2">
              <h3 className="font-label-md text-label-md text-on-surface font-bold uppercase tracking-wider">Waiting on Others</h3>
              <span className="bg-surface-container-highest px-2 py-0.5 rounded text-[11px] font-bold">{waiting.length}</span>
            </div>
            <button className="text-on-surface-variant hover:text-primary"><span className="material-symbols-outlined text-[18px]">more_horiz</span></button>
          </div>
          <div className="kanban-column p-2 rounded-xl flex flex-col gap-4">
            {waiting.map(t => renderTaskCard(t, "WAITING"))}
          </div>
        </div>

        {/* Column: In Progress */}
        <div className="flex flex-col gap-4 min-w-[280px]">
          <div className="flex items-center justify-between px-2">
            <div className="flex items-center gap-2">
              <h3 className="font-label-md text-label-md text-on-surface font-bold uppercase tracking-wider">In Progress</h3>
              <span className="bg-primary px-2 py-0.5 rounded text-[11px] text-white font-bold">{inProgress.length}</span>
            </div>
            <button className="text-on-surface-variant hover:text-primary"><span className="material-symbols-outlined text-[18px]">more_horiz</span></button>
          </div>
          <div className="kanban-column p-2 rounded-xl flex flex-col gap-4">
            {inProgress.map(t => renderTaskCard(t, "IN_PROGRESS"))}
          </div>
        </div>

        {/* Column: Completed */}
        <div className="flex flex-col gap-4 min-w-[280px]">
          <div className="flex items-center justify-between px-2">
            <div className="flex items-center gap-2">
              <h3 className="font-label-md text-label-md text-on-surface font-bold uppercase tracking-wider">Completed</h3>
              <span className="bg-surface-container-highest px-2 py-0.5 rounded text-[11px] font-bold">{completed.length}</span>
            </div>
            <button className="text-on-surface-variant hover:text-primary"><span className="material-symbols-outlined text-[18px]">more_horiz</span></button>
          </div>
          <div className="kanban-column p-2 rounded-xl flex flex-col gap-4 opacity-70">
            {completed.map(t => renderTaskCard(t, "DONE"))}
          </div>
        </div>
      </div>
    </>
  );
}
