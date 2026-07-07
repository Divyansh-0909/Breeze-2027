"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Roles } from "@prisma/client";
import { addUser, deleteUser } from "./actions";

export default function UsersPage() {
  const [users, setUsers] = useState<Roles[]>([]);
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState("");
  const [isAddingUser, setIsAddingUser] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    const data = await fetch("/api/breeze-admin/users");
    const obj = await data.json();
    setUsers(obj.data);
  };
  const handleAddUser = async () => {
    setIsAddingUser(true);
    try {
      const success = await addUser(newEmail, newPassword, newRole);
      if (success) {
        fetchUsers();
        setNewEmail("");
        setNewPassword("");
        setNewRole("user");
      }
    } finally {
      setIsAddingUser(false);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    const success = await deleteUser(userId);
    if (success) {
      fetchUsers();
    }
  };
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Manage Users</h1>
        <Dialog>
          <DialogTrigger asChild>
            <Button>Add User</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New User</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="club">Club</Label>
                <Select value={newRole} onValueChange={setNewRole}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="breeze">Breeze</SelectItem>
                    <SelectItem value="e-cell">E-Cell</SelectItem>
                    <SelectItem value="acm">ACM</SelectItem>
                    <SelectItem value="feeding india snioe chapter">Feeding India SNIoE Chapter</SelectItem>
                    <SelectItem value="the mathematics society">The Mathematics Society</SelectItem>
                    <SelectItem value="nexus">Nexus</SelectItem>
                    <SelectItem value="gdsc">GDSC</SelectItem>
                    <SelectItem value="cineu">CineU</SelectItem>
                    <SelectItem value="aura">AURA</SelectItem>
                    <SelectItem value="finvest">Finvest</SelectItem>
                    <SelectItem value="celestia explora">Celestia Explora</SelectItem>
                    <SelectItem value="kalakriti">Kalakriti</SelectItem>
                    <SelectItem value="snuphoria">Snuphoria</SelectItem>
                    <SelectItem value="words.ink">Words.Ink</SelectItem>
                    <SelectItem value="girlup">GirlUP</SelectItem>
                    <SelectItem value="snu queer collective">SNU Queer Collective</SelectItem>
                    <SelectItem value="imprints">Imprints</SelectItem>
                    <SelectItem value="sigree">Sigree</SelectItem>
                    <SelectItem value="inferno">Inferno</SelectItem>
                    <SelectItem value="the chemistry society">The Chemistry Society</SelectItem>
                    <SelectItem value="mythiya">Mythiya</SelectItem>
                    <SelectItem value="the economics society">The Economics Society</SelectItem>
                    <SelectItem value="adventure club">Adventure Club</SelectItem>
                    <SelectItem value="design club">Design Club</SelectItem>
                    <SelectItem value="spic macay">Spic Macay</SelectItem>
                    <SelectItem value="pixels">Pixels</SelectItem>
                    <SelectItem value="munsoc">MUNSOC</SelectItem>
                    <SelectItem value="the active dreams">The Active Dreams</SelectItem>
                    <SelectItem value="wula">Wula</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button onClick={handleAddUser} disabled={isAddingUser}>
                {isAddingUser ? "Adding..." : "Add User"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Email</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {users.map((user, i) => (
            <TableRow key={i}>
              <TableCell>{user.email}</TableCell>
              <TableCell className="capitalize">{user.club_name}</TableCell>
              <TableCell>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleDeleteUser(user.id)}
                >
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
