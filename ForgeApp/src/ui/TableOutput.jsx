import React from "react";

const TableOutput = ({ tableData }) => {
  if (!tableData) return null;

  const { headers, rows } = tableData;

  return (
    <div style={{ marginTop: 20 }}>
      <h4>📋 Generated Output</h4>
      <table
        border="1"
        cellPadding="6"
        style={{ borderCollapse: "collapse", width: "100%" }}
      >
        <thead>
          <tr>
            {headers.map((h, i) => (
              <th key={i}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TableOutput;
