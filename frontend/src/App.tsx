import React, { useState } from "react";
import { ApolloProvider } from "@apollo/client";
import { client } from "./client.ts";
import { PatientList } from "./components/PatientList.tsx";
import { PatientDetail } from "./components/PatientDetail.tsx";
import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(
    null
  );

  return (
    <ApolloProvider client={client}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<PatientList />} />
          <Route path="/patient/:id" element={<PatientDetail />} />
        </Routes>
      </BrowserRouter>
    </ApolloProvider>
  );
}

export default App;
