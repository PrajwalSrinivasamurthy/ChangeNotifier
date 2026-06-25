"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function SettingsPanel() {
  const [phone, setPhone] = useState("");
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getSettings().then((s) => setPhone(s.recipient_phone_number || ""));
  }, []);

  const save = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await api.updateSettings(phone.trim());
      setSaved(true);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-2 max-w-md">
      <h2 className="font-semibold text-lg">SMS recipient</h2>
      <p className="text-sm text-foreground/60">
        Phone number (E.164 format, e.g. +18065551234) that receives change alerts.
      </p>
      <div className="flex gap-2">
        <input
          className="border border-border bg-background text-foreground rounded-lg px-3 py-1.5 flex-1 placeholder:text-foreground/40 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="+18065551234"
          value={phone}
          onChange={(e) => {
            setPhone(e.target.value);
            setSaved(false);
          }}
        />
        <button
          className="px-3 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
          onClick={save}
          disabled={saving}
        >
          {saving ? "Saving..." : "Save"}
        </button>
      </div>
      {saved && <p className="text-sm text-green-500">Saved.</p>}
    </div>
  );
}
