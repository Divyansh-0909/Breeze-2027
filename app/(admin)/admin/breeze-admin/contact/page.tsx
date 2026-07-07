"use client";

import { useEffect, useState } from "react";
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
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface ContactSubmission {
  id: string;
  created_at: string;
  name: string;
  email: string;
  phone: string;
  message: string;
}

export default function ContactSubmissionsPage() {
  const [submissions, setSubmissions] = useState<ContactSubmission[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubmission, setSelectedSubmission] = useState<ContactSubmission | null>(null);

  useEffect(() => {
    fetchSubmissions();
  }, []);

  const fetchSubmissions = async () => {
    try {
      const response = await fetch("/api/contact");
      const data = await response.json();
      setSubmissions(data);
    } catch (error) {
      console.error("Failed to fetch submissions:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">Loading submissions...</p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Contact Form Submissions</h1>
      
      {submissions.length === 0 ? (
        <p className="text-gray-500">No contact submissions yet.</p>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Phone</TableHead>
                <TableHead>Message</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {submissions.map((submission) => (
                <TableRow key={submission.id}>
                  <TableCell className="whitespace-nowrap">
                    {new Date(submission.created_at).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </TableCell>
                  <TableCell className="font-medium">{submission.name}</TableCell>
                  <TableCell>
                    <a
                      href={`mailto:${submission.email}`}
                      className="text-blue-600 hover:underline"
                    >
                      {submission.email}
                    </a>
                  </TableCell>
                  <TableCell>{submission.phone}</TableCell>
                  <TableCell className="max-w-[200px] truncate">
                    {submission.message}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedSubmission(submission)}
                    >
                      View Full
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Full Message Dialog */}
      <Dialog open={!!selectedSubmission} onOpenChange={() => setSelectedSubmission(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Message from {selectedSubmission?.name}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="font-medium">{selectedSubmission?.email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Phone</p>
              <p className="font-medium">{selectedSubmission?.phone}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Message</p>
              <p className="whitespace-pre-wrap bg-gray-50 p-3 rounded-lg">
                {selectedSubmission?.message}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Submitted</p>
              <p className="font-medium">
                {selectedSubmission && new Date(selectedSubmission.created_at).toLocaleDateString("en-IN", {
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
