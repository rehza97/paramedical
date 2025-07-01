import React from "react";

const Table = ({ columns, data, emptyMessage = "Aucune donnée disponible." }) => (
  <div className="overflow-x-auto rounded shadow">
    <table className="min-w-full table-auto border-collapse">
      <thead>
        <tr>
          {columns.map((col) => (
            <th
              key={col.accessor}
              className="px-4 py-2 border-b bg-gray-50 text-left font-semibold"
            >
              {col.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.length > 0 ? (
          data.map((row, i) => {
            const rowKey = row.id || `row-${i}`;
            return (
              <tr key={rowKey} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                {columns.map((col) => (
                  <td key={`${rowKey}-${col.accessor}`} className="px-4 py-2 border-b">
                    {row[col.accessor]}
                  </td>
                ))}
              </tr>
            );
          })
        ) : (
          <tr>
            <td colSpan={columns.length} className="text-center py-4 text-gray-500">
              {emptyMessage}
            </td>
          </tr>
        )}
      </tbody>
    </table>
  </div>
);

export default Table;
