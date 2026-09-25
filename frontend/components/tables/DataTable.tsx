import { formatCellValue } from "@/lib/utils";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface DataTableProps {
  columns: string[];
  rows: Record<string, unknown>[];
  maxRows?: number;
}

export function DataTable({ columns, rows, maxRows = 100 }: DataTableProps) {
  if (!columns.length) {
    return <p className="py-6 text-center text-sm text-muted-foreground">No data to display.</p>;
  }

  const visibleRows = rows.slice(0, maxRows);

  return (
    <div className="rounded-lg border border-border">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((col) => (
              <TableHead key={col}>{col.replaceAll("_", " ")}</TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {visibleRows.map((row, i) => (
            <TableRow key={i}>
              {columns.map((col) => (
                <TableCell key={col}>{formatCellValue(row[col])}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {rows.length > maxRows && (
        <p className="border-t border-border px-3 py-2 text-xs text-muted-foreground">
          Showing {maxRows} of {rows.length} rows.
        </p>
      )}
    </div>
  );
}
