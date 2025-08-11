import React from "react";
import { useQuery, gql } from "@apollo/client";
import {
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Button,
  Stack,
} from "@mui/material";
import { useParams, useNavigate } from "react-router-dom";

export const GET_PATIENT = gql`
  query GetPatient($patientId: Int!) {
    patient(id: $patientId) {
      patientId
      firstName
      lastName
      dob
      email
      phone
      address
      appointments {
        appointmentId
        appointmentDate
        appointmentType
      }
    }
  }
`;

type Appointment = {
  appointmentId: number;
  appointmentDate: string;
  appointmentType: string;
};

type PatientDetail = {
  patientId: number;
  firstName: string;
  lastName: string;
  dob: string;
  email: string;
  phone: string;
  address: string;
  appointments: Appointment[];
};

export function PatientDetail() {
  const params = useParams();
  const navigate = useNavigate();

  const patientId = parseInt(params.id!);
  const { loading, error, data } = useQuery<{ patient: PatientDetail }>(
    GET_PATIENT,
    {
      variables: { patientId },
    }
  );

  if (loading) return <p>Loading patient detail...</p>;
  if (error) return <p>Error loading patient detail</p>;

  if (!data) {
    return <p>Error loading patient detail</p>;
  }

  const patient = data.patient;

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Stack direction="row" justifyContent="space-between" mb={2}>
        <Button
          color="primary"
          variant="outlined"
          onClick={() => navigate("/")}
        >
          Back to Patient List
        </Button>
      </Stack>

      <Box mt={3}>
        <Typography variant="h5">{`${patient.firstName} ${patient.lastName}`}</Typography>
        <Typography>
          DOB: {new Date(patient.dob).toLocaleDateString()}
        </Typography>
        <Typography>Email: {patient.email}</Typography>
        <Typography>Phone: {patient.phone}</Typography>
        <Typography>Address: {patient.address}</Typography>

        <Typography variant="h6" mt={3} mb={3}>
          Appointments
        </Typography>
        {patient.appointments.length < 1 && (
          <Box>
            <Typography>This patient does not have any appointments</Typography>
          </Box>
        )}
        {patient.appointments.length > 0 && (
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Appointment ID</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Type</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {patient.appointments.map((appt) => (
                  <TableRow key={appt.appointmentId}>
                    <TableCell>{appt.appointmentId}</TableCell>
                    <TableCell>
                      {appt.appointmentDate
                        ? new Date(appt.appointmentDate).toLocaleDateString()
                        : "N/A"}
                    </TableCell>
                    <TableCell>{appt.appointmentType}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </Container>
  );
}
