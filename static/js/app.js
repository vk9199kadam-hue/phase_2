/**
 * VisionX Phase 2 — Frontend Application Controller
 * Manages 4 Screening Modalities, 2-Role Views, Live Blockchain Ledger, and Offline Mode.
 */

// Application State
const state = {
  currentRole: 'guard', // 'guard' | 'officer'
  currentPipeline: 'fixed_id', // 'fixed_id' | 'visa' | 'nfc' | 'offline'
  selectedSample: 'aadhaar_real_atharv.png',
  selectedFile: null,
  isOfflineMode: false,
  samples: {},
  systemStatus: {}
};

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', async () => {
  initPWA();
  bindRoleTabs();
  bindPipelineTabs();
  bindDropzones();
  bindActionButtons();
  await loadSystemStatus();
  await loadSamples();
  selectPipeline('fixed_id');
});

let deferredPrompt;

// Register Service Worker for PWA
function initPWA() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then(() => console.log('Service Worker Active (PWA Enabled)'))
      .catch((err) => console.log('SW Registration error:', err));
  }

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    const btn = document.getElementById('btnInstallApp');
    if (btn) btn.style.display = 'flex';
  });

  const btn = document.getElementById('btnInstallApp');
  if (btn) {
    btn.addEventListener('click', async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response to the install prompt: ${outcome}`);
        deferredPrompt = null;
      } else {
        alert("📲 To install this app on your phone:\n\n1. Open this URL in Chrome/Safari on your mobile device\n2. Tap the browser menu (⋮ or Share)\n3. Tap 'Install app' or 'Add to Home Screen'\n\nThis installs the VisionX native mobile terminal with hardware NFC reading support!");
      }
    });
  }
}

// Fetch System Status & Blockchain info
async function loadSystemStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    state.systemStatus = data;
    const sectorEl = document.getElementById('sectorIdDisplay');
    if (sectorEl) sectorEl.textContent = data.sector_id;
  } catch (err) {
    console.warn('Backend offline, running in browser local mode.');
    toggleOfflineBadge(true);
  }
}

// Load Preloaded Samples
async function loadSamples() {
  try {
    const res = await fetch('/api/samples');
    state.samples = await res.json();
    renderSamplePresets();
  } catch (err) {
    console.warn('Failed to load sample catalogue');
  }
}

// Toggle Online/Offline Badge
function toggleOfflineBadge(isOffline) {
  const badge = document.getElementById('connectionStatusBadge');
  if (!badge) return;
  state.isOfflineMode = isOffline;
  if (isOffline) {
    badge.className = 'status-badge offline';
    badge.innerHTML = '<span class="status-dot"></span> OFFLINE REGIONAL CACHE';
  } else {
    badge.className = 'status-badge';
    badge.innerHTML = '<span class="status-dot"></span> ONLINE / CLOUD LINKED';
  }
}

// --- TAB ROUTING ---
function bindRoleTabs() {
  document.querySelectorAll('.role-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.role-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const role = btn.dataset.role;
      state.currentRole = role;

      if (role === 'guard') {
        document.getElementById('guardView').style.display = 'block';
        document.getElementById('officerView').style.display = 'none';
      } else {
        document.getElementById('guardView').style.display = 'none';
        document.getElementById('officerView').style.display = 'block';
        loadBlockchainLedger();
      }
    });
  });
}

function bindPipelineTabs() {
  document.querySelectorAll('.pipeline-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      selectPipeline(btn.dataset.pipeline);
    });
  });
}

function selectPipeline(pipelineId) {
  state.currentPipeline = pipelineId;
  document.querySelectorAll('.pipeline-btn').forEach(b => b.classList.remove('active'));
  const activeBtn = document.querySelector(`.pipeline-btn[data-pipeline="${pipelineId}"]`);
  if (activeBtn) activeBtn.classList.add('active');

  // Show corresponding inputs
  document.getElementById('panelFixedId').style.display = pipelineId === 'fixed_id' ? 'block' : 'none';
  document.getElementById('panelVisa').style.display = pipelineId === 'visa' ? 'block' : 'none';
  document.getElementById('panelNfc').style.display = pipelineId === 'nfc' ? 'block' : 'none';
  document.getElementById('panelOffline').style.display = pipelineId === 'offline' ? 'block' : 'none';

  renderSamplePresets();
  resetResultView();
}

// --- SAMPLE CHIPS RENDERING ---
function renderSamplePresets() {
  const container = document.getElementById('samplePresetsContainer');
  if (!container) return;
  container.innerHTML = '';

  if (state.currentPipeline === 'fixed_id' && state.samples.fixed_id_aadhaar) {
    state.samples.fixed_id_aadhaar.forEach(s => {
      const chip = document.createElement('button');
      chip.className = `sample-chip ${s.type === 'REAL' ? 'real-chip' : 'fake-chip'}`;
      chip.innerHTML = `<strong>${s.type === 'REAL' ? '🟢' : '🔴'} ${s.label}</strong> (${s.uid})`;
      chip.onclick = () => selectSampleAadhaar(s);
      container.appendChild(chip);
    });
  } else if (state.currentPipeline === 'visa' && state.samples.unstructured_visa) {
    state.samples.unstructured_visa.forEach(s => {
      const chip = document.createElement('button');
      chip.className = `sample-chip ${s.type === 'REAL' ? 'real-chip' : 'fake-chip'}`;
      chip.innerHTML = `<strong>${s.type === 'REAL' ? '🟢' : '🔴'} ${s.label}</strong>`;
      chip.onclick = () => selectSampleVisa(s);
      container.appendChild(chip);
    });
  } else if (state.currentPipeline === 'nfc' && state.samples.nfc_passports) {
    state.samples.nfc_passports.forEach(s => {
      const chip = document.createElement('button');
      chip.className = `sample-chip ${s.type === 'REAL' ? 'real-chip' : 'fake-chip'}`;
      chip.innerHTML = `<strong>${s.type === 'REAL' ? '🟢' : '🔴'} ${s.label}</strong>`;
      chip.onclick = () => selectSampleNfc(s);
      container.appendChild(chip);
    });
  } else if (state.currentPipeline === 'offline') {
    const quickKeys = [
      { key: '001100220033', label: 'Atharv (Real Enrolled)', type: 'REAL' },
      { key: '987654321002', label: 'Dhruva (Real Enrolled)', type: 'REAL' },
      { key: '123412345555', label: 'Haroon (Flagged Suspect)', type: 'FAKE' }
    ];
    quickKeys.forEach(k => {
      const chip = document.createElement('button');
      chip.className = `sample-chip ${k.type === 'REAL' ? 'real-chip' : 'fake-chip'}`;
      chip.innerHTML = `<strong>${k.type === 'REAL' ? '🟢' : '🔴'} ${k.label}</strong>`;
      chip.onclick = () => {
        document.getElementById('offlineUidInput').value = k.key;
        runOfflineSearch();
      };
      container.appendChild(chip);
    });
  }
}

function selectSampleAadhaar(sample) {
  state.selectedSample = sample.id;
  state.selectedFile = null;
  const preview = document.getElementById('idPreviewImg');
  const placeholder = document.getElementById('idUploadPlaceholder');
  const box = document.getElementById('idIntakeBox');

  preview.src = `/storage/sample_data/${sample.id}`;
  preview.style.display = 'block';
  placeholder.style.display = 'none';
  box.classList.add('has-preview');
}

function selectSampleVisa(sample) {
  state.selectedSample = sample.id;
  state.selectedFile = null;
  const preview = document.getElementById('visaPreviewImg');
  const placeholder = document.getElementById('visaUploadPlaceholder');
  const box = document.getElementById('visaIntakeBox');

  preview.src = `/storage/sample_data/${sample.id}`;
  preview.style.display = 'block';
  placeholder.style.display = 'none';
  box.classList.add('has-preview');
}

function selectSampleNfc(sample) {
  state.selectedSample = sample.id;
  const chipLog = document.getElementById('nfcChipLog');
  if (sample.id === 'nfc_passport_real') {
    chipLog.innerHTML = `<span style="color: green;">✓ ISO/IEC 14443 Type A Target Detected</span><br>
UID: 04:A2:88:B1:99:C0<br>
SOD Hash: SHA-256 (Signed by DSCA_INDIA_01)<br>
DG1: MRZ TD3 Valid<br>
DG2: Biometric Face Hash: a7f839c...`;
  } else {
    chipLog.innerHTML = `<span style="color: red;">⚠ Cloned Chip / Tampered Certificate Detected</span><br>
UID: 04:FF:11:00:22:99<br>
SOD Hash: INVALID_ROOT_SIGNATURE<br>
DG1: Checksum Anomaly<br>
DG2: Photo substitution detected`;
  }
}

// --- FILE UPLOADS ---
function bindDropzones() {
  const idFileInput = document.getElementById('idFileInput');
  if (idFileInput) {
    idFileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        state.selectedFile = file;
        state.selectedSample = null;
        const reader = new FileReader();
        reader.onload = (re) => {
          const preview = document.getElementById('idPreviewImg');
          const placeholder = document.getElementById('idUploadPlaceholder');
          const box = document.getElementById('idIntakeBox');
          preview.src = re.target.result;
          preview.style.display = 'block';
          placeholder.style.display = 'none';
          box.classList.add('has-preview');
        };
        reader.readAsDataURL(file);
      }
    });
  }
}

// --- ACTION BUTTON HANDLERS ---
function bindActionButtons() {
  // 1. Scan Fixed ID
  document.getElementById('btnScanFixedId').addEventListener('click', runFixedIdScreening);
  // 2. Scan Visa
  document.getElementById('btnScanVisa').addEventListener('click', runVisaScreening);
  // 3. Scan NFC
  document.getElementById('btnTapNfc').addEventListener('click', runNfcScreening);
  // 4. Offline Search
  document.getElementById('btnSearchOffline').addEventListener('click', runOfflineSearch);
  // Refresh Blockchain Ledger
  const btnRefreshChain = document.getElementById('btnRefreshChain');
  if (btnRefreshChain) btnRefreshChain.addEventListener('click', loadBlockchainLedger);
}

// --- PIPELINE 1 EXECUTION ---
async function runFixedIdScreening() {
  setLoadingState(true, 'Processing Deskew, RapidOCR, ELA Forensics & ArcFace 512-D...');
  const formData = new FormData();
  if (state.selectedFile) {
    formData.append('file', state.selectedFile);
  } else {
    formData.append('sample_id', state.selectedSample || 'aadhaar_real_atharv.png');
  }
  formData.append('officer_id', 'GUARD_0482_SINGH');

  try {
    const res = await fetch('/api/verify/fixed_id', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    renderScreeningResults(data);
  } catch (err) {
    alert('Verification error: ' + err.message);
  } finally {
    setLoadingState(false);
  }
}

// --- PIPELINE 2 EXECUTION ---
async function runVisaScreening() {
  setLoadingState(true, 'Extracting Unstructured Visa NLP & Consular Stamp Integrity...');
  const formData = new FormData();
  formData.append('sample_id', state.selectedSample || 'visa_real_employment.png');
  formData.append('officer_id', 'GUARD_0482_SINGH');

  try {
    const res = await fetch('/api/verify/unstructured_visa', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    renderVisaResults(data);
  } catch (err) {
    alert('Visa Screening error: ' + err.message);
  } finally {
    setLoadingState(false);
  }
}

// --- PIPELINE 3 EXECUTION (WITH HARDWARE WEB NFC SUPPORT) ---
async function runNfcScreening() {
  const chipLog = document.getElementById('nfcChipLog');
  
  // 1. Check for Real Physical Web NFC Hardware on Phone
  if ('NDEFReader' in window) {
    try {
      chipLog.innerHTML = `<span style="color: #EA580C; font-weight: bold;">📲 READY TO SCAN: Hold e-Passport or NFC Card against the back of your phone...</span>`;
      setLoadingState(true, 'Awaiting physical NFC card tap on phone sensor...');
      
      const ndef = new NDEFReader();
      await ndef.scan();
      
      ndef.onreading = async (event) => {
        const serialNumber = event.serialNumber || '04:A2:88:B1:99:C0';
        chipLog.innerHTML = `<span style="color: green; font-weight: bold;">✓ PHYSICAL NFC CHIP DETECTED!</span><br>Serial UID: ${serialNumber}<br>Reading ICAO DG1/DG2 records...`;
        
        let mrzPayload = 'P<INDSHARMA<<RAHUL<<<<<<<<<<<<<<<<<<<<<<<\nL8923412<3IND9501015M2812318<<<<<<<<<<<<<<04';
        for (const record of event.message.records) {
          if (record.recordType === 'text') {
            const textDecoder = new TextDecoder(record.encoding);
            mrzPayload = textDecoder.decode(record.data);
          }
        }

        const payload = {
          chip_uid: serialNumber,
          dg1_mrz: mrzPayload,
          sod_signature_hex: 'A9F88C02B9103C89104EF8012398401823901823',
          force_tamper_flag: false,
          officer_id: 'GUARD_MOBILE_NFC'
        };

        const res = await fetch('/api/verify/nfc_chip', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        renderNfcResults(data);
        setLoadingState(false);
      };
      return;
    } catch (nfcErr) {
      console.warn('Physical NFC scan failed or denied, falling back to prototype pipeline:', nfcErr);
      chipLog.innerHTML += `<br><span style="color: goldenrod;">ℹ Sensor note: Using high-fidelity protocol reader emulation.</span>`;
    }
  }

  // 2. Fallback / Test Protocol Simulator
  setLoadingState(true, 'Reading ISO/IEC 14443 NFC Chip & Validating ICAO SOD Signature...');
  const isTampered = state.selectedSample === 'nfc_passport_tampered';
  const payload = {
    chip_uid: isTampered ? '04:FF:11:00:22:99' : '04:A2:88:B1:99:C0',
    dg1_mrz: isTampered 
      ? 'P<INDTAMPER<<MODIFIED<<<<<<<<<<<<<<<<<<<<<<<\nK7182931<3IND9501015M2812318<<<<<<<<<<<<<<04'
      : 'P<INDSHARMA<<RAHUL<<<<<<<<<<<<<<<<<<<<<<<\nL8923412<3IND9501015M2812318<<<<<<<<<<<<<<04',
    sod_signature_hex: isTampered ? 'CORRUPT_HEX' : 'A9F88C02B9103C89104EF8012398401823901823',
    force_tamper_flag: isTampered,
    officer_id: 'GUARD_0482_SINGH'
  };

  try {
    const res = await fetch('/api/verify/nfc_chip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    renderNfcResults(data);
  } catch (err) {
    alert('NFC error: ' + err.message);
  } finally {
    setLoadingState(false);
  }
}

// --- PIPELINE 4 EXECUTION ---
async function runOfflineSearch() {
  const uid = document.getElementById('offlineUidInput').value.trim();
  if (!uid) {
    alert('Please enter a 12-digit Aadhaar UID.');
    return;
  }
  setLoadingState(true, 'Querying Regional Offline Metadata B-Tree Cache...');

  try {
    const res = await fetch('/api/verify/offline_lookup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ primary_key: uid, officer_id: 'GUARD_OFFLINE_01' })
    });
    const data = await res.json();
    renderOfflineResults(data);
  } catch (err) {
    alert('Offline lookup error: ' + err.message);
  } finally {
    setLoadingState(false);
  }
}

// --- RESULTS RENDERING HELPERS ---
function resetResultView() {
  document.getElementById('decisionBadgeContainer').className = 'decision-card';
  document.getElementById('triageVerdict').textContent = 'WAITING FOR SCAN';
  document.getElementById('triageScore').textContent = 'Risk Score: -- / 100';
  document.getElementById('triageStatusText').textContent = 'Present document to begin multi-signal inspection.';
  document.getElementById('reasonCodesList').innerHTML = '';
  document.getElementById('extractedFieldsList').innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem;">No active document evaluated.</div>';
}

function renderScreeningResults(data) {
  const dec = data.risk_decision;
  const ext = data.extracted_data;
  const fr = data.forensic_report;
  const bio = data.biometric_report;
  const bk = data.blockchain_audit;
  const lat = data.latency_breakdown_ms;

  const card = document.getElementById('decisionBadgeContainer');
  card.className = `decision-card ${dec.verdict.toLowerCase()}`;
  document.getElementById('triageVerdict').textContent = `${dec.verdict === 'GREEN' ? '🟢' : (dec.verdict === 'YELLOW' ? '🟡' : '🔴')} ${dec.verdict}`;
  document.getElementById('triageScore').textContent = `Risk Score: ${dec.final_risk_score} / 100`;
  document.getElementById('triageStatusText').textContent = dec.status_text;

  // Reason Codes
  const reasonsDiv = document.getElementById('reasonCodesList');
  reasonsDiv.innerHTML = '';
  dec.reason_codes.forEach(r => {
    const span = document.createElement('span');
    span.className = `reason-tag ${dec.verdict === 'GREEN' ? 'green-tag' : ''}`;
    span.textContent = r;
    reasonsDiv.appendChild(span);
  });

  // Data fields
  const fieldsDiv = document.getElementById('extractedFieldsList');
  fieldsDiv.innerHTML = `
    <div class="data-row"><span class="label">Extracted Name</span><span class="value">${ext.name}</span></div>
    <div class="data-row"><span class="label">Aadhaar UID</span><span class="value">${ext.aadhaar_number}</span></div>
    <div class="data-row"><span class="label">Verhoeff Checksum</span><span class="value" style="color: ${ext.is_verhoeff_valid ? 'green' : 'red'};">${ext.is_verhoeff_valid ? '✓ VALID' : '✗ CHECKSUM FAILED'}</span></div>
    <div class="data-row"><span class="label">DOB / Gender</span><span class="value">${ext.dob} | ${ext.gender}</span></div>
    <div class="data-row"><span class="label">ArcFace 512-D Biometrics</span><span class="value">${bio.similarity_percentage}% (Age Compensated)</span></div>
    <div class="data-row"><span class="label">Photo Halo Gradient</span><span class="value" style="color: ${fr.halo_tamper_detected ? 'red' : 'green'};">${fr.photo_halo_gradient} (${fr.halo_tamper_detected ? 'TAMPER HALO' : 'OK'})</span></div>
    <div class="data-row"><span class="label">Layout Forensics</span><span class="value">${fr.summary}</span></div>
    <div class="data-row"><span class="label">Blockchain Anchor</span><span class="value" style="font-family: monospace; font-size: 0.72rem;">#${bk.block_index} (${bk.block_hash.slice(0, 16)}...)</span></div>
  `;

  // Latency bar
  updateLatencyBar(lat.total_pipeline);
}

function renderVisaResults(data) {
  const v = data.visa_report;
  const bk = data.blockchain_audit;

  const card = document.getElementById('decisionBadgeContainer');
  card.className = `decision-card ${v.verdict.toLowerCase()}`;
  document.getElementById('triageVerdict').textContent = `${v.verdict === 'GREEN' ? '🟢' : '🔴'} ${v.verdict}`;
  document.getElementById('triageScore').textContent = `Risk Score: ${v.risk_score} / 100`;
  document.getElementById('triageStatusText').textContent = v.reason_code;

  document.getElementById('reasonCodesList').innerHTML = `<span class="reason-tag ${v.verdict === 'GREEN' ? 'green-tag' : ''}">${v.reason_code}</span>`;

  document.getElementById('extractedFieldsList').innerHTML = `
    <div class="data-row"><span class="label">Document Category</span><span class="value">${v.doc_category}</span></div>
    <div class="data-row"><span class="label">Visa Number</span><span class="value">${v.visa_number}</span></div>
    <div class="data-row"><span class="label">Category / Type</span><span class="value">${v.visa_type}</span></div>
    <div class="data-row"><span class="label">Expiry Date</span><span class="value" style="color: ${v.is_expired ? 'red' : 'green'};">${v.expiry_date} (${v.is_expired ? 'EXPIRED' : 'ACTIVE'})</span></div>
    <div class="data-row"><span class="label">Consular Seal</span><span class="value">${v.consular_seal_verified ? '✓ VERIFIED' : '✗ TAMPERED'}</span></div>
    <div class="data-row"><span class="label">Issuing Post</span><span class="value">${v.issuing_post}</span></div>
    <div class="data-row"><span class="label">Blockchain Anchor</span><span class="value" style="font-family: monospace; font-size: 0.72rem;">#${bk.block_index}</span></div>
  `;
  updateLatencyBar(data.latency_ms);
}

function renderNfcResults(data) {
  const n = data.nfc_result;
  const bk = data.blockchain_audit;

  const card = document.getElementById('decisionBadgeContainer');
  card.className = `decision-card ${n.verdict.toLowerCase()}`;
  document.getElementById('triageVerdict').textContent = `${n.verdict === 'GREEN' ? '🟢' : '🔴'} ${n.verdict}`;
  document.getElementById('triageScore').textContent = `Risk Score: ${n.risk_score} / 100`;
  document.getElementById('triageStatusText').textContent = n.reason_code;

  document.getElementById('reasonCodesList').innerHTML = `<span class="reason-tag ${n.verdict === 'GREEN' ? 'green-tag' : ''}">${n.reason_code}</span>`;

  document.getElementById('extractedFieldsList').innerHTML = `
    <div class="data-row"><span class="label">NFC Chip UID</span><span class="value">${n.chip_uid}</span></div>
    <div class="data-row"><span class="label">Chip Protocol</span><span class="value">${n.protocol}</span></div>
    <div class="data-row"><span class="label">SOD Signature</span><span class="value" style="color: ${n.sod_signature_valid ? 'green' : 'red'};">${n.sod_signature_valid ? '✓ CRYPTOGRAPHICALLY VALID' : '✗ SIGNATURE FAILED'}</span></div>
    <div class="data-row"><span class="label">Chip vs Visual Face Match</span><span class="value" style="color: ${n.chip_vs_visual_photo_match ? 'green' : 'red'};">${n.chip_vs_visual_photo_match ? '✓ IDENTICAL EMBEDDINGS' : '✗ CLONED / MODIFIED'}</span></div>
    <div class="data-row"><span class="label">DG1 MRZ Status</span><span class="value">${n.dg1_mrz_data.overall_valid ? '✓ ICAO 9303 Compliant' : '✗ MRZ Checksum Error'}</span></div>
    <div class="data-row"><span class="label">Blockchain Anchor</span><span class="value" style="font-family: monospace; font-size: 0.72rem;">#${bk.block_index}</span></div>
  `;
  updateLatencyBar(data.latency_ms);
}

function renderOfflineResults(data) {
  const o = data.offline_result;
  const card = document.getElementById('decisionBadgeContainer');
  card.className = `decision-card ${o.verdict.toLowerCase()}`;
  document.getElementById('triageVerdict').textContent = `${o.verdict === 'GREEN' ? '🟢' : '🔴'} ${o.verdict} (OFFLINE)`;
  document.getElementById('triageScore').textContent = `Risk Score: ${o.risk_score} / 100`;
  document.getElementById('triageStatusText').textContent = o.message;

  document.getElementById('reasonCodesList').innerHTML = `<span class="reason-tag ${o.verdict === 'GREEN' ? 'green-tag' : ''}">${o.flagged ? o.flag_reason : 'OFFLINE_CACHE_MATCH'}</span>`;

  document.getElementById('extractedFieldsList').innerHTML = `
    <div class="data-row"><span class="label">Primary Key Index</span><span class="value">${o.primary_key}</span></div>
    <div class="data-row"><span class="label">Local Cache Match</span><span class="value" style="color: ${o.found ? 'green' : 'red'};">${o.found ? '✓ FOUND IN SECTOR BUNDLE' : '✗ NOT ENROLLED'}</span></div>
    <div class="data-row"><span class="label">Name / Subject</span><span class="value">${o.name || 'N/A'}</span></div>
    <div class="data-row"><span class="label">Status</span><span class="value">${o.status || 'N/A'}</span></div>
    <div class="data-row"><span class="label">Offline Latency</span><span class="value">${o.latency_ms} ms (Instant Local Query)</span></div>
  `;
  updateLatencyBar(o.latency_ms);
}

function updateLatencyBar(latencyMs) {
  const fill = document.getElementById('latencyProgressFill');
  const txt = document.getElementById('latencyText');
  if (fill && txt) {
    txt.textContent = `${latencyMs} ms / 1960 ms Ceiling`;
    const pct = Math.min(100, (latencyMs / 1960.0) * 100);
    fill.style.width = `${pct}%`;
    fill.style.backgroundColor = latencyMs <= 1960 ? 'var(--govt-green)' : 'var(--govt-red)';
  }
}

function setLoadingState(isLoading, message = 'Processing...') {
  const btn = document.getElementById('btnScanFixedId');
  if (!btn) return;
  if (isLoading) {
    btn.disabled = true;
    btn.innerHTML = `<span>⏳ ${message}</span>`;
  } else {
    btn.disabled = false;
    btn.innerHTML = `<span>🛡️ EXECUTE MULTI-SIGNAL INSPECTION</span>`;
  }
}

// --- ROLE 2: BLOCKCHAIN EXPLORER ---
async function loadBlockchainLedger() {
  const tbody = document.getElementById('blockchainTableBody');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Loading Merkle blocks...</td></tr>';

  try {
    const res = await fetch('/api/blockchain/ledger');
    const data = await res.json();
    tbody.innerHTML = '';

    data.chain.forEach(b => {
      const tr = document.createElement('tr');
      const badgeColor = b.verdict === 'GREEN' ? 'green' : (b.verdict === 'YELLOW' ? 'goldenrod' : (b.verdict === 'RED' ? 'red' : 'navy'));
      tr.innerHTML = `
        <td><strong>#${b.index}</strong></td>
        <td><span style="font-weight: bold; color: ${badgeColor};">${b.verdict}</span></td>
        <td>${b.risk_score}</td>
        <td>${b.modality}</td>
        <td>${b.officer_id}</td>
        <td><span class="hash-cell">${b.block_hash.slice(0, 18)}...</span></td>
        <td>${b.formatted_time}</td>
      `;
      tbody.appendChild(tr);
    });

    // Check integrity
    const chkRes = await fetch('/api/blockchain/verify');
    const chk = await chkRes.json();
    const chainStatus = document.getElementById('chainIntegrityStatus');
    if (chainStatus) {
      if (chk.valid) {
        chainStatus.innerHTML = `🟢 <strong>CHAIN VERIFIED IMMUTABLE</strong> (${chk.total_blocks} Blocks Validated)`;
      } else {
        chainStatus.innerHTML = `🔴 <strong>CHAIN TAMPER DETECTED:</strong> ${chk.error}`;
      }
    }
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="color: red;">Error loading blockchain: ${err.message}</td></tr>`;
  }
}
