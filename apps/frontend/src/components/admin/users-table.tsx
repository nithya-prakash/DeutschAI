import type { UserRead } from "@/types/api";

export function UsersTable({ users }: { users: UserRead[] }) {
  if (users.length === 0) {
    return <p className="text-sm text-muted-foreground">No users yet.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-border text-xs uppercase tracking-wide text-muted-foreground">
            <th className="py-2 pr-4 font-medium">Email</th>
            <th className="py-2 pr-4 font-medium">Name</th>
            <th className="py-2 pr-4 font-medium">CEFR</th>
            <th className="py-2 pr-4 font-medium">Joined</th>
            <th className="py-2 pr-4 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} className="border-b border-border last:border-0">
              <td className="py-2 pr-4">{u.email}</td>
              <td className="py-2 pr-4">{u.full_name}</td>
              <td className="py-2 pr-4">{u.cefr_level}</td>
              <td className="py-2 pr-4">{new Date(u.created_at).toLocaleDateString()}</td>
              <td className="py-2 pr-4">
                {u.is_superuser ? "Admin" : u.is_active ? "Active" : "Inactive"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
