"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Roles } from "@prisma/client";
import { addUser, deleteUser } from "./actions";
import { Plus, Trash2 } from "lucide-react";
import { mergeClubs } from "@/lib/clubs";

const ALL_CLUBS = mergeClubs();

export default function UsersPage() {
  const [users, setUsers] = useState<Roles[]>([]);
  const [loading, setLoading] = useState(true);
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState("");
  const [isAddingUser, setIsAddingUser] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);

  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => { fetchUsers(); }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await fetch("/api/breeze-admin/users");
      const obj = await data.json();
      setUsers(obj.data || []);
    } finally {
      setLoading(false);
    }
  };

  const isFormValid = Boolean(newEmail.trim() && newPassword.trim() && newRole);

  const handleAddUser = async () => {
    if (!isFormValid) return;
    setIsAddingUser(true);
    try {
      const success = await addUser(newEmail, newPassword, newRole);
      if (success) {
        fetchUsers();
        setNewEmail(""); setNewPassword(""); setNewRole("");
        setDialogOpen(false);
      }
    } finally {
      setIsAddingUser(false);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    setDeletingId(userId);
    try {
      const success = await deleteUser(userId);
      if (success) fetchUsers();
    } finally {
      setDeletingId(null);
    }
  };

  const inputStyle = { background: '#0a0a0a', border: '1px solid #262626', color: '#e5e5e5' };

  return (
    <div className="px-8 py-6 max-w-[1200px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-[18px] font-semibold tracking-[-0.02em]" style={{ color: '#e5e5e5' }}>Users</h1>
          <p className="text-[13px] mt-0.5" style={{ color: '#666' }}>Manage admin accounts and club roles</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <button
              className="flex items-center gap-1.5 px-3 py-[6px] rounded-md text-[13px] font-medium transition-colors duration-100 cursor-pointer"
              style={{ background: '#e5e5e5', color: '#0a0a0a' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = '#d4d4d4'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = '#e5e5e5'; }}
            >
              <Plus size={14} strokeWidth={2} />
              Add User
            </button>
          </DialogTrigger>
          <DialogContent className="max-w-[400px] p-0 gap-0" style={{ background: '#141414', border: '1px solid #1e1e1e', color: '#e5e5e5' }}>
            <DialogHeader className="px-5 py-4" style={{ borderBottom: '1px solid #1e1e1e' }}>
              <DialogTitle className="text-[15px] font-semibold" style={{ color: '#e5e5e5' }}>Add User</DialogTitle>
            </DialogHeader>
            <div className="p-5 space-y-4">
              <div className="space-y-1.5">
                <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="email">
                  Email <span style={{ color: '#f87171' }}>*</span>
                </Label>
                <Input id="email" value={newEmail} onChange={(e) => setNewEmail(e.target.value)} placeholder="Enter email address" className="h-8 text-[13px] rounded-md" style={inputStyle} />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="password">
                  Password <span style={{ color: '#f87171' }}>*</span>
                </Label>
                <Input id="password" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="Enter password" className="h-8 text-[13px] rounded-md" style={inputStyle} />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[12px] font-medium" style={{ color: '#aaa' }} htmlFor="club">
                  Club <span style={{ color: '#f87171' }}>*</span>
                </Label>
                <Select value={newRole} onValueChange={setNewRole}>
                  <SelectTrigger className="h-9 text-[13px] rounded-md font-medium border border-[#383842] bg-[#18181c] text-[#f4f4f5]">
                    <SelectValue placeholder="Select club" />
                  </SelectTrigger>
                  <SelectContent className="max-h-[280px] border border-[#383842] bg-[#18181c] text-[#f4f4f5] shadow-2xl">
                    {ALL_CLUBS.map((club) => (
                      <SelectItem key={club.id} value={club.club_name}>
                        {club.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex gap-2 pt-2" style={{ borderTop: '1px solid #1e1e1e' }}>
                <Button disabled={isAddingUser} onClick={() => setDialogOpen(false)} className="flex-1 h-8 text-[13px] font-medium rounded-md cursor-pointer" style={{ background: 'transparent', border: '1px solid #262626', color: '#888' }}>Cancel</Button>
                <Button
                  onClick={handleAddUser}
                  disabled={isAddingUser || !isFormValid}
                  className="flex-1 h-8 text-[13px] font-medium rounded-md transition-all duration-150"
                  style={{
                    background: isFormValid ? '#e5e5e5' : '#262626',
                    color: isFormValid ? '#0a0a0a' : '#666',
                    cursor: isFormValid && !isAddingUser ? 'pointer' : 'not-allowed',
                    opacity: isAddingUser ? 0.7 : 1,
                  }}
                >
                  {isAddingUser ? (
                    <span className="flex items-center justify-center gap-1.5">
                      <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Adding…
                    </span>
                  ) : (
                    "Add User"
                  )}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="flex items-center gap-6 mb-6 px-4 py-3 rounded-lg" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Total Users</p>
          <p className="text-[20px] font-semibold" style={{ color: '#e5e5e5' }}>{users.length}</p>
        </div>
      </div>

      {/* User list */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <p className="text-[13px]" style={{ color: '#555' }}>Loading users…</p>
        </div>
      ) : users.length === 0 ? (
        <div className="flex items-center justify-center py-16">
          <p className="text-[13px]" style={{ color: '#555' }}>No users found</p>
        </div>
      ) : (
        <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #1e1e1e' }}>
          <div className="grid grid-cols-[2fr_1.5fr_60px] gap-3 px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider" style={{ background: '#141414', color: '#555', borderBottom: '1px solid #1e1e1e' }}>
            <div>Email</div>
            <div>Club</div>
            <div></div>
          </div>
          {users.map((user, i) => (
            <div
              key={i}
              className="grid grid-cols-[2fr_1.5fr_60px] gap-3 px-4 py-3 items-center transition-colors duration-75"
              style={{ borderBottom: '1px solid #1a1a1a' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = '#141414'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
            >
              <div className="text-[13px] truncate" style={{ color: '#e5e5e5' }}>{user.email}</div>
              <div>
                <span className="text-[11px] px-2 py-0.5 rounded-full font-medium capitalize" style={{ background: '#1a1a1a', color: '#888', border: '1px solid #262626' }}>
                  {user.club_name}
                </span>
              </div>
              <div className="flex justify-end">
                <button
                  disabled={deletingId === user.id}
                  onClick={() => handleDeleteUser(user.id)}
                  className="p-1.5 rounded transition-colors duration-100 cursor-pointer disabled:opacity-50"
                  style={{ color: '#666' }}
                  onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(248,113,113,0.1)'; e.currentTarget.style.color = '#f87171'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#666'; }}
                >
                  {deletingId === user.id ? (
                    <svg className="animate-spin h-3.5 w-3.5 text-[#f87171]" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  ) : (
                    <Trash2 size={13} />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
