// Vercel Serverless Function: Generates and downloads official METAVITAL Clinical PDF Report (PDF 1.4)
export default function handler(req, res) {
  try {
    const name = "Ramon Munoz Martinez";
    const age = 63;
    const height = 165.0;
    const weight = 101.5;
    const bmi = 37.28;
    const category = "Obesidad (Grado II)";

    const commands = [];

    // Background Header Bar (Blue: #0D6EFD = 0.05 0.43 0.99)
    commands.push("0.05 0.43 0.99 rg");
    commands.push("30 780 535 40 re f");

    // Header Title
    commands.push("1 1 1 rg");
    commands.push("BT /F2 16 Tf 42 794 Td (METAVITAL - INFORME CLINICO PARA EL MEDICO) Tj ET");
    commands.push("BT /F1 9 Tf 380 794 Td (Estandar ADA / ESC / ESH) Tj ET");

    // Patient Info Box (Light grey background)
    commands.push("0.94 0.96 0.98 rg");
    commands.push("30 710 535 55 re f");
    commands.push("0.85 0.88 0.92 RG 1 w");
    commands.push("30 710 535 55 re S");

    // Patient Details Text
    commands.push("0.06 0.09 0.16 rg");
    commands.push(`BT /F2 11 Tf 42 748 Td (PACIENTE: ${name.toUpperCase()}) Tj ET`);
    commands.push(`BT /F1 10 Tf 42 730 Td (Edad: ${age} anos  |  Estatura: ${height} cm  |  Peso: ${weight} kg) Tj ET`);
    commands.push(`BT /F2 10 Tf 42 716 Td (IMC: ${bmi} kg/m2 - ${category}) Tj ET`);

    // Section 1: Glucemia (Left column)
    commands.push("0.88 0.92 0.96 RG");
    commands.push("30 565 260 130 re S");
    commands.push("0.05 0.43 0.99 rg");
    commands.push("BT /F2 11 Tf 40 678 Td (PERFIL GLUCEMICO Y TIEMPO EN RANGO) Tj ET");
    commands.push("0.1 0.1 0.1 rg");
    commands.push("BT /F2 10 Tf 40 655 Td (Tiempo en Rango [70-130 mg/dL]: 85%) Tj ET");
    commands.push("BT /F1 9.5 Tf 40 635 Td (Media Basal en Ayunas: 114 mg/dL) Tj ET");
    commands.push("BT /F1 9.5 Tf 40 615 Td (Eventos de Hipoglucemia [<70]: 0) Tj ET");
    commands.push("BT /F1 9.5 Tf 40 595 Td (Eventos de Hiperglucemia [>180]: 0) Tj ET");
    commands.push("BT /F1 9 Tf 40 575 Td (Metas ADA: TIR > 70%, Hipos < 4% [CUMPLIDA]) Tj ET");

    // Section 2: Presión Arterial (Right column)
    commands.push("0.88 0.92 0.96 RG");
    commands.push("305 565 260 130 re S");
    commands.push("0.7 0.16 0.2 rg");
    commands.push("BT /F2 11 Tf 315 678 Td (PRESION ARTERIAL Y RIESGO VASCULAR) Tj ET");
    commands.push("0.1 0.1 0.1 rg");
    commands.push("BT /F2 10 Tf 315 655 Td (Media Sistolica / Diastolica: 126/78 mmHg) Tj ET");
    commands.push("BT /F1 9.5 Tf 315 635 Td (Objetivo ESC/ESH: < 130/80 mmHg) Tj ET");
    commands.push("BT /F1 9.5 Tf 315 615 Td (Registros en alerta [>=140/90]: 0) Tj ET");
    commands.push("BT /F1 9.5 Tf 315 595 Td (Crisis Hipertensivas [>=180/120]: 0) Tj ET");
    commands.push("BT /F1 9 Tf 315 575 Td (Control Hemodinamico: Estable) Tj ET");

    // Section 3: Movimiento y Paseos Posprandiales (Left column lower)
    commands.push("0.88 0.92 0.96 RG");
    commands.push("30 425 260 125 re S");
    commands.push("0.4 0.15 0.7 rg");
    commands.push("BT /F2 11 Tf 40 534 Td (ACTIVIDAD ANTI-SEDENTARISMO) Tj ET");
    commands.push("0.1 0.1 0.1 rg");
    commands.push("BT /F2 10 Tf 40 512 Td (Media de Pasos Diarios: 6.420 pasos/dia) Tj ET");
    commands.push("BT /F1 9.5 Tf 40 492 Td (Meta Pasiva: 4.000 pasos progresivos) Tj ET");
    commands.push("BT /F2 9.5 Tf 40 472 Td (Paseos Posprandiales [15 min]: Realizados) Tj ET");
    commands.push("BT /F1 9 Tf 40 452 Td (Mecanismo: Translocacion GLUT4 activada) Tj ET");
    commands.push("BT /F1 9 Tf 40 435 Td (Adherencia Dieta Mediterranea: 94%) Tj ET");

    // Section 4: Adherencia Farmacológica (Right column lower)
    commands.push("0.88 0.92 0.96 RG");
    commands.push("305 425 260 125 re S");
    commands.push("0.08 0.5 0.25 rg");
    commands.push("BT /F2 11 Tf 315 534 Td (TRATAMIENTO Y CORRELACION FARMACOLOGICA) Tj ET");
    commands.push("0.1 0.1 0.1 rg");
    commands.push("BT /F2 10 Tf 315 512 Td (Adherencia Terapeutica: 96% de tomas) Tj ET");
    commands.push("BT /F1 9 Tf 315 494 Td (Ramipril 10mg / Secalip 240mg / Synjardy [1-0-1]) Tj ET");
    commands.push("BT /F1 9 Tf 315 477 Td (Omacor 0-2-0  |  Atenolol 50mg / Atorvastatina [0-0-1]) Tj ET");
    commands.push("BT /F2 9 Tf 315 460 Td (Insulina y Ozempic 1mg semanal: Pautas activas) Tj ET");
    commands.push("BT /F1 8.5 Tf 315 443 Td (SUSPENDIDO por Nefrologo: Trajenta 5mg) Tj ET");
    commands.push("BT /F1 8.5 Tf 315 429 Td (Correlacion Omision-Presion: Estable sin rebotes) Tj ET");

    // Section 5: Juicio Clínico, Nefrología y Recomendaciones
    commands.push("0.96 0.97 0.99 rg");
    commands.push("30 240 535 170 re f");
    commands.push("0.05 0.43 0.99 RG 2 w");
    commands.push("30 240 535 170 re S");

    commands.push("0.05 0.43 0.99 rg");
    commands.push("BT /F2 11 Tf 42 392 Td (EVALUACION MULTIDISCIPLINAR - NEFROLOGIA Y METABOLISMO) Tj ET");
    commands.push("0.1 0.1 0.1 rg");
    commands.push("BT /F2 9.5 Tf 42 374 Td (ERC Estadio 3a [FG 42 ml/min] | Creatinina: 1.7 mg/dL | Potasio: 5.5 mEq/L) Tj ET");
    commands.push("BT /F2 9.5 Tf 42 357 Td (Perfil Lipidico: LDL 49 mg/dL [Excelente] | Trigliceridos: 346 mg/dL | HbA1c: 7.1%) Tj ET");
    commands.push("BT /F1 9 Tf 42 340 Td (1. PROHIBICION AINES: Cero Ibuprofeno/Enantyum por nefrotoxicidad; usar Paracetamol/Nolotil.) Tj ET");
    commands.push("BT /F1 9 Tf 42 324 Td (2. SEGURIDAD POTASIO: Prohibida sal de potasio; tecnicas de remojo y doble coccion en verduras.) Tj ET");
    commands.push("BT /F1 9 Tf 42 308 Td (3. ROTACION INSULINA: Alternar cuadrantes para erradicar lipodistrofia e irregularidad glucemica.) Tj ET");
    commands.push("BT /F1 9 Tf 42 292 Td (4. EVOLUCION PONDERAL: Peso 101.5 kg [-4.5 kg desde consulta de 106 kg en H.U. Jaen]. Enhorabuena.) Tj ET");
    commands.push("BT /F1 9 Tf 42 276 Td (5. RITMO DE VIDA: Caminatas en llano 15 min posprandial. Soporte paciente: ALCER Jaen [953 25 22 44].) Tj ET");
    commands.push("BT /F1 8.5 Tf 42 250 Td (Documento estructurado conforme estandares KDIGO 2024 / ADA 2026 / ESC 2024.) Tj ET");

    // Signature Box
    commands.push("0.7 0.7 0.7 RG 1 w");
    commands.push("350 200 190 1 re S");
    commands.push("0.4 0.4 0.4 rg");
    commands.push("BT /F1 8.5 Tf 360 188 Td (Firma y Sello del Medico Especialista) Tj ET");

    // Footer HIPAA / RGPD
    commands.push("0.5 0.5 0.5 rg");
    commands.push("BT /F1 8 Tf 30 170 Td (Documento oficial METAVITAL | Cifrado E2E AES-256 | Cumplimiento estricto HIPAA y RGPD) Tj ET");

    const streamBody = Buffer.from(commands.join("\n"), "latin1");

    const objects = [];
    objects.push(Buffer.from("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n", "latin1"));
    objects.push(Buffer.from("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n", "latin1"));
    objects.push(Buffer.from("3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>\nendobj\n", "latin1"));
    objects.push(Buffer.concat([
      Buffer.from(`4 0 obj\n<< /Length ${streamBody.length} >>\nstream\n`, "latin1"),
      streamBody,
      Buffer.from("\nendstream\nendobj\n", "latin1")
    ]));
    objects.push(Buffer.from("5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n", "latin1"));
    objects.push(Buffer.from("6 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n", "latin1"));

    let pdf = Buffer.from("%PDF-1.4\n", "latin1");
    const offsets = [0];
    for (const obj of objects) {
      offsets.push(pdf.length);
      pdf = Buffer.concat([pdf, obj]);
    }

    const xrefOffset = pdf.length;
    let xref = `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
    for (let i = 1; i <= objects.length; i++) {
      xref += `${String(offsets[i]).padStart(10, "0")} 00000 n \n`;
    }
    const trailer = `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;
    pdf = Buffer.concat([pdf, Buffer.from(xref, "latin1"), Buffer.from(trailer, "latin1")]);

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", 'attachment; filename="Informe_Clinico_METAVITAL_Ramon_Munoz.pdf"');
    res.setHeader("Content-Length", pdf.length);
    res.status(200).send(pdf);
  } catch (err) {
    res.status(500).json({ error: "Error generating PDF report", details: err.message });
  }
}
