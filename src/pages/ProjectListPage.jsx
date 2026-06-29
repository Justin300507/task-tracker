import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function ProjectListPage() {
  const [projects, setProjects] = useState([]);
  const [limit, setLimit] = useState(50);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/projects?limit=${limit}&offset=${offset}`);
      if (!response.ok) {
        throw new Error("Failed to fetch projects");
      }
      const data = await response.json();
      // Expecting response shape: { items: [...], total: number }
      setProjects(data.items ?? []);
      setTotal(data.total ?? 0);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [limit, offset]);

  const totalPages = Math.ceil(total / limit) || 1;
  const currentPage = Math.floor(offset / limit) + 1;

  const goToPage = (page) => {
    const newOffset = (page - 1) * limit;
    setOffset(newOffset);
  };

  return (
    <div>
      <h1>Projects</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((proj) => (
                <tr key={proj.id}>
                  <td>{proj.id}</td>
                  <td>
                    <Link to={`/projects/${proj.id}`}>{proj.name}</Link>
                  </td>
                  <td>{proj.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: "1rem" }}>
            <button onClick={() => goToPage(1)} disabled={currentPage === 1}>First</button>
            <button onClick={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>Prev</button>
            <span>
              Page {currentPage} of {totalPages}
            </span>
            <button onClick={() => goToPage(currentPage + 1)} disabled={currentPage === totalPages}>Next</button>
            <button onClick={() => goToPage(totalPages)} disabled={currentPage === totalPages}>Last</button>
          </div>
        </>
      )}
    </div>
  );
}

export default ProjectListPage;
