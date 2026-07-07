"use client";
import Link from "next/link";
import { createClient } from "@/utils/supabase/client";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const supabase = createClient();

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/admin/login");
  };

  return (
    <div className="flex min-h-screen">
      <div className="w-64 bg-white border-r border-gray-200 shadow-sm flex flex-col">
        <nav className="p-4 space-y-2 flex-1">
          <Link
            href="/admin/breeze-admin"
            className="flex items-center px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg transition-colors"
          >
            Pending Transactions
          </Link>
          <Link
            href="/admin/breeze-admin/approved"
            className="flex items-center px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg transition-colors"
          >
            Approved Transactions
          </Link>
          <Link
            href="/admin/breeze-admin/events"
            className="flex items-center px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg transition-colors"
          >
            Manage Events
          </Link>
          <Link
            href="/admin/breeze-admin/contact"
            className="flex items-center px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg transition-colors"
          >
            Contact Submissions
          </Link>
          <Link
            href="/admin/breeze-admin/download"
            className="flex items-center px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg transition-colors"
          >
            Data Download
          </Link>
        </nav>
        <div className="p-4 border-t border-gray-200">
          <Button
            onClick={handleLogout}
            variant="destructive"
            className="w-full px-4 py-2 rounded-lg"
          >
            Logout
          </Button>
        </div>
      </div>
      <div className="flex-1 p-8">{children}</div>
    </div>
  );
}
