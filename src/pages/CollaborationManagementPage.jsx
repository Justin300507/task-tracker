import React, { useEffect, useState } from "react";
import { Container, Typography, Box, CircularProgress, Alert, Table, TableHead, TableRow, TableCell, TableBody, Button } from "@mui/material";

const CollaborationManagementPage = () => {
  const [collaborations, setCollaborations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("/api/collaborations");
        if (!response.ok) {
          throw new Error(`Error ${response.status}`);
        }
        const data = await response.json();
        setCollaborations(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    setError(null);
    setCollaborations([]);
    // Re-trigger fetch by re-running effect
    // Simple approach: call fetchData again
    (async () => {
      try {
        const response = await fetch("/api/collaborations");
        if (!response.ok) {
          throw new Error(`Error ${response.status}`);
        }
        const data = await response.json();
        setCollaborations(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography component="h1" variant="h4">
          Collaboration Management
        </Typography>
        <Button variant="contained" color="primary" onClick={handleRefresh} disabled={loading}>
          Refresh
        </Button>
      </Box>
      {loading && (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      )}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {!loading && !error && collaborations.length === 0 && (
        <Alert severity="info">No collaboration records found.</Alert>
      )}
      {!loading && collaborations.length > 0 && (
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Created At</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {collaborations.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item.id}</TableCell>
                <TableCell>{item.name}</TableCell>
                <TableCell>{item.description}</TableCell>
                <TableCell>{new Date(item.created_at).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Container>
  );
};

export default CollaborationManagementPage;
