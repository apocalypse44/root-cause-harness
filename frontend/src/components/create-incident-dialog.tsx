"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { api } from "@/lib/api";
import type { Severity } from "@/lib/types";

export function CreateIncidentDialog() {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [serviceId, setServiceId] = useState("");
  const [severity, setSeverity] = useState<Severity>("medium");
  const queryClient = useQueryClient();

  const { data: services } = useQuery({ queryKey: ["services"], queryFn: api.services.list });

  const mutation = useMutation({
    mutationFn: api.incidents.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      setOpen(false);
      setTitle("");
    },
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>
        Create Incident
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Incident</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <Input placeholder="Incident title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <Select value={serviceId} onValueChange={(v) => setServiceId(v ?? "")}>
            <SelectTrigger><SelectValue placeholder="Select service" /></SelectTrigger>
            <SelectContent>
              {services?.map((s) => (
                <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={severity} onValueChange={(v) => setSeverity((v ?? "medium") as Severity)}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              {["low", "medium", "high", "critical"].map((s) => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button onClick={() => mutation.mutate({ service_id: serviceId, title, severity })} disabled={!title || !serviceId}>
            Create
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
