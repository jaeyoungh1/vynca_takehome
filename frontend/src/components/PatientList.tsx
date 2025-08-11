import React from "react";
import { useQuery, gql, useMutation, useLazyQuery } from "@apollo/client";
import {
  Container,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Button,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

export const GET_PATIENTS = gql`
  query GetPatients {
    patients {
      patientId
      firstName
      lastName
      dob
      phone
      appointments {
        id
      }
    }
  }
`;

// For loading demo data
const UPLOAD_DEMO_DATA = gql`
  mutation {
    uploadDemoData {
      success
      message
    }
  }
`;
const CHECK_DATA = gql`
  query {
    patients {
      patientId
    }
  }
`;

type Patient = {
  patientId: number;
  firstName: string;
  lastName: string;
  dob: string;
  phone: string;
  appointments: { id: number }[];
};

export function PatientList() {
  const [checkData] = useLazyQuery(CHECK_DATA);
  const [uploadDemoData] = useMutation(UPLOAD_DEMO_DATA);

  const handleClick = async () => {
    try {
      const { data } = await checkData();
      const hasData = data?.patients?.length > 0;

      if (hasData) {
        window.alert("Demo data already loaded");
        return;
      }

      const result = await uploadDemoData();
      const { success } = result.data.uploadDemoData;

      if (success) {
        window.alert(`Demo data loaded! :)`);
        window.location.reload();
      } else {
        window.alert(`Error loading demo data`);
      }
    } catch (err) {
      console.error(err);
      window.alert("Error connecting to the backend");
    }
  };

  const { loading, error, data } = useQuery<{ patients: Patient[] }>(
    GET_PATIENTS
  );
  const navigate = useNavigate();

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error</p>;

  function handleSelectPatient(id: number) {
    navigate(`/patient/${id}`);
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 1 }}>
      <Box sx={{ my: 4, textAlign: "center" }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Mini Clinical Dashboard
        </Typography>
      </Box>
      <Button variant="contained" sx={{ mb: 2 }} onClick={handleClick}>
        Load Demo Data
      </Button>
      <TableContainer component={Paper}>
        <Typography variant="h6" sx={{ m: 2 }}>
          Patient List
        </Typography>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Last Name</TableCell>
              <TableCell>First Name</TableCell>
              <TableCell>DOB</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Appointment Count</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data!.patients.map((patient) => (
              <TableRow
                key={patient.patientId}
                hover
                onClick={() => handleSelectPatient(patient.patientId)}
                sx={{ cursor: "pointer" }}
              >
                <TableCell>{`${patient.lastName}`}</TableCell>
                <TableCell>{`${patient.firstName}`}</TableCell>
                <TableCell>
                  {new Date(patient.dob).toLocaleDateString()}
                </TableCell>
                <TableCell>{patient.phone}</TableCell>
                <TableCell>{patient.appointments.length}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
}
