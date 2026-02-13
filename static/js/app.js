/* ============================================
   HR Analytics — Application JavaScript
   ============================================ */
(function () {
    'use strict';

    /* ---------- CONFIG ---------- */
    const API = {
        health: '/health',
        predict: '/predict',
    };

    /* ---------- FIELD DEFINITIONS ---------- */
    const FIELDS = {
        sirh: [
            { key: 'age', label: 'Age', type: 'number', min: 18, max: 70, default: 35 },
            { key: 'genre', label: 'Genre', type: 'select', options: ['M', 'F'], labels: { M: 'Homme', F: 'Femme' }, default: 'M' },
            { key: 'revenu_mensuel', label: 'Revenu mensuel', type: 'number', min: 1, step: 100, default: 5000 },
            { key: 'statut_marital', label: 'Statut marital', type: 'select', options: ['Célibataire', 'Marié(e)', 'Divorcé(e)'], default: 'Marié(e)' },
            { key: 'departement', label: 'Département', type: 'select', options: ['Commercial', 'Consulting', 'Ressources Humaines'], default: 'Consulting' },
            { key: 'poste', label: 'Poste', type: 'select', options: ['Cadre Commercial', 'Assistant de Direction', 'Consultant', 'Manager', 'Tech Lead', 'Représentant Commercial', 'Directeur Technique', 'Senior Manager', 'Ressources Humaines'], default: 'Consultant' },
            { key: 'nombre_experiences_precedentes', label: 'Experiences precedentes', type: 'number', min: 0, default: 2 },
            { key: 'nombre_heures_travailless', label: 'Heures travaillees (mensuel)', type: 'number', min: 0, step: 1, default: 80 },
            { key: 'annee_experience_totale', label: 'Annees experience totale', type: 'number', min: 0, default: 10 },
            { key: 'annees_dans_l_entreprise', label: 'Annees dans l\'entreprise', type: 'number', min: 0, default: 5 },
            { key: 'annees_dans_le_poste_actuel', label: 'Annees dans le poste actuel', type: 'number', min: 0, default: 3 },
        ],
        eval: [
            { key: 'satisfaction_employee_environnement', label: 'Satisfaction environnement', type: 'rating', min: 1, max: 5, default: 4 },
            { key: 'note_evaluation_precedente', label: 'Note evaluation precedente', type: 'rating', min: 1, max: 5, default: 3 },
            { key: 'niveau_hierarchique_poste', label: 'Niveau hierarchique', type: 'rating', min: 1, max: 5, default: 2 },
            { key: 'satisfaction_employee_nature_travail', label: 'Satisfaction nature travail', type: 'rating', min: 1, max: 5, default: 4 },
            { key: 'satisfaction_employee_equipe', label: 'Satisfaction equipe', type: 'rating', min: 1, max: 5, default: 4 },
            { key: 'satisfaction_employee_equilibre_pro_perso', label: 'Equilibre pro/perso', type: 'rating', min: 1, max: 5, default: 3 },
            { key: 'note_evaluation_actuelle', label: 'Note evaluation actuelle', type: 'rating', min: 1, max: 5, default: 3 },
            { key: 'heure_supplementaires', label: 'Heures supplementaires', type: 'toggle', options: ['Oui', 'Non'], default: 'Non' },
            { key: 'augementation_salaire_precedente', label: 'Augmentation salaire precedente', type: 'slider', min: 0, max: 100, unit: '%', default: 15 },
        ],
        sondage: [
            { key: 'nombre_participation_pee', label: 'Participations PEE', type: 'number', min: 0, default: 1 },
            { key: 'nb_formations_suivies', label: 'Formations suivies', type: 'number', min: 0, default: 3 },
            { key: 'nombre_employee_sous_responsabilite', label: 'Employes sous responsabilite', type: 'number', min: 0, default: 1 },
            { key: 'distance_domicile_travail', label: 'Distance domicile-travail (km)', type: 'number', min: 0, default: 10 },
            { key: 'niveau_education', label: 'Niveau education', type: 'rating', min: 1, max: 5, default: 3 },
            { key: 'domaine_etude', label: 'Domaine d\'etude', type: 'select', options: ['Infra & Cloud', 'Transformation Digitale', 'Marketing', 'Autre', 'Entrepreunariat', 'Ressources Humaines'], default: 'Transformation Digitale' },
            { key: 'frequence_deplacement', label: 'Frequence de deplacement', type: 'select', options: ['Occasionnel', 'Frequent', 'Aucun'], default: 'Occasionnel' },
            { key: 'annees_depuis_la_derniere_promotion', label: 'Annees depuis derniere promotion', type: 'number', min: 0, default: 2 },
            { key: 'annes_sous_responsable_actuel', label: 'Annees sous responsable actuel', type: 'number', min: 0, default: 3 },
        ],
    };

    /* Hidden field */
    const HIDDEN = { ayant_enfants: 'Y' };

    /* ---------- STATE ---------- */
    let currentStep = 0;
    const totalSteps = 4;

    /* ---------- DOM REFS ---------- */
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const dom = {
        hero: $('#hero'),
        formSection: $('#form-section'),
        resultSection: $('#result-section'),
        startBtn: $('#start-btn'),
        form: $('#predict-form'),
        btnPrev: $('#btn-prev'),
        btnNext: $('#btn-next'),
        btnSubmit: $('#btn-submit'),
        btnNew: $('#btn-new'),
        loadingOverlay: $('#loading-overlay'),
        healthBadge: $('#health-badge'),
        healthText: $('.health-text'),
        themeToggle: $('#theme-toggle'),
        stepperProgress: $('#stepper-progress'),
        gaugeValue: $('#gauge-value'),
        gaugeFill: $('#gauge-fill'),
        resultBadge: $('#result-badge'),
        resultLabel: $('#result-label'),
        resultInterp: $('#result-interpretation'),
        reviewSummary: $('#review-summary'),
    };

    /* ---------- THEME ---------- */
    function initTheme() {
        dom.themeToggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('hr-theme', next);
        });
    }

    /* ---------- HEALTH CHECK ---------- */
    async function checkHealth() {
        try {
            const res = await fetch(API.health);
            const data = await res.json();
            dom.healthBadge.className = 'health-badge health-badge--ok';
            dom.healthText.textContent = data.model_loaded ? 'Systeme operationnel' : 'Modele non charge';
            if (!data.model_loaded) dom.healthBadge.className = 'health-badge health-badge--error';
        } catch {
            dom.healthBadge.className = 'health-badge health-badge--error';
            dom.healthText.textContent = 'API indisponible';
        }
    }

    /* ---------- FIELD RENDERING ---------- */
    function renderField(field) {
        const wrapper = document.createElement('div');
        wrapper.className = 'field';

        const label = document.createElement('label');
        label.className = 'field-label';
        label.textContent = field.label;
        label.setAttribute('for', 'f-' + field.key);
        wrapper.appendChild(label);

        switch (field.type) {
            case 'number': {
                const input = document.createElement('input');
                input.type = 'number';
                input.id = 'f-' + field.key;
                input.className = 'field-input';
                input.name = field.key;
                input.value = field.default;
                if (field.min !== undefined) input.min = field.min;
                if (field.max !== undefined) input.max = field.max;
                if (field.step) input.step = field.step;
                wrapper.appendChild(input);
                break;
            }
            case 'select': {
                const select = document.createElement('select');
                select.id = 'f-' + field.key;
                select.className = 'field-input';
                select.name = field.key;
                field.options.forEach(opt => {
                    const option = document.createElement('option');
                    option.value = opt;
                    option.textContent = field.labels ? (field.labels[opt] || opt) : opt;
                    if (opt === field.default) option.selected = true;
                    select.appendChild(option);
                });
                wrapper.appendChild(select);
                break;
            }
            case 'rating': {
                const group = document.createElement('div');
                group.className = 'rating-group';
                group.dataset.key = field.key;
                for (let i = field.min; i <= field.max; i++) {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'rating-btn' + (i === field.default ? ' active' : '');
                    btn.dataset.value = i;
                    btn.textContent = i;
                    btn.addEventListener('click', () => {
                        group.querySelectorAll('.rating-btn').forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                    });
                    group.appendChild(btn);
                }
                wrapper.appendChild(group);
                break;
            }
            case 'toggle': {
                const wrap = document.createElement('div');
                wrap.className = 'toggle-wrap';
                const toggle = document.createElement('button');
                toggle.type = 'button';
                toggle.className = 'toggle' + (field.default === field.options[0] ? ' active' : '');
                toggle.dataset.key = field.key;
                toggle.dataset.on = field.options[0];
                toggle.dataset.off = field.options[1];
                const toggleLabel = document.createElement('span');
                toggleLabel.className = 'toggle-label';
                toggleLabel.textContent = field.default === field.options[0] ? field.options[0] : field.options[1];
                toggle.addEventListener('click', () => {
                    toggle.classList.toggle('active');
                    toggleLabel.textContent = toggle.classList.contains('active') ? field.options[0] : field.options[1];
                });
                wrap.appendChild(toggle);
                wrap.appendChild(toggleLabel);
                wrapper.appendChild(wrap);
                break;
            }
            case 'slider': {
                const wrap = document.createElement('div');
                wrap.className = 'slider-wrap';
                const row = document.createElement('div');
                row.className = 'slider-row';
                const slider = document.createElement('input');
                slider.type = 'range';
                slider.className = 'slider';
                slider.id = 'f-' + field.key;
                slider.name = field.key;
                slider.min = field.min;
                slider.max = field.max;
                slider.value = field.default;
                const valSpan = document.createElement('span');
                valSpan.className = 'slider-value';
                valSpan.textContent = field.default + (field.unit || '');
                slider.addEventListener('input', () => {
                    valSpan.textContent = slider.value + (field.unit || '');
                });
                row.appendChild(slider);
                row.appendChild(valSpan);
                wrap.appendChild(row);
                wrapper.appendChild(wrap);
                break;
            }
        }
        return wrapper;
    }

    function renderAllFields() {
        Object.entries(FIELDS).forEach(([section, fields]) => {
            const container = document.getElementById('fields-' + section);
            if (!container) return;
            fields.forEach(field => container.appendChild(renderField(field)));
        });
    }

    /* ---------- FORM DATA COLLECTION ---------- */
    function collectFormData() {
        const data = { ...HIDDEN };

        Object.values(FIELDS).flat().forEach(field => {
            switch (field.type) {
                case 'number': {
                    const el = document.getElementById('f-' + field.key);
                    const v = parseFloat(el.value);
                    data[field.key] = Number.isInteger(field.default) ? Math.round(v) : v;
                    break;
                }
                case 'select': {
                    const el = document.getElementById('f-' + field.key);
                    data[field.key] = el.value;
                    break;
                }
                case 'rating': {
                    const group = document.querySelector(`.rating-group[data-key="${field.key}"]`);
                    const active = group.querySelector('.rating-btn.active');
                    data[field.key] = active ? parseInt(active.dataset.value) : field.default;
                    break;
                }
                case 'toggle': {
                    const toggle = document.querySelector(`.toggle[data-key="${field.key}"]`);
                    data[field.key] = toggle.classList.contains('active') ? toggle.dataset.on : toggle.dataset.off;
                    break;
                }
                case 'slider': {
                    const el = document.getElementById('f-' + field.key);
                    data[field.key] = parseInt(el.value);
                    break;
                }
            }
        });

        return data;
    }

    /* ---------- REVIEW PANEL ---------- */
    function renderReview() {
        const data = collectFormData();
        const sections = [
            { title: 'Profil RH (SIRH)', fields: FIELDS.sirh },
            { title: 'Evaluations (EVAL)', fields: FIELDS.eval },
            { title: 'Sondage', fields: FIELDS.sondage },
        ];

        dom.reviewSummary.innerHTML = '';
        sections.forEach(section => {
            const group = document.createElement('div');
            group.className = 'review-group';
            const title = document.createElement('div');
            title.className = 'review-group-title';
            title.textContent = section.title;
            group.appendChild(title);

            section.fields.forEach(field => {
                const item = document.createElement('div');
                item.className = 'review-item';
                const labelEl = document.createElement('span');
                labelEl.className = 'review-item-label';
                labelEl.textContent = field.label;
                const valueEl = document.createElement('span');
                valueEl.className = 'review-item-value';
                let val = data[field.key];
                if (field.type === 'select' && field.labels) val = field.labels[val] || val;
                if (field.unit) val = val + field.unit;
                valueEl.textContent = val;
                item.appendChild(labelEl);
                item.appendChild(valueEl);
                group.appendChild(item);
            });
            dom.reviewSummary.appendChild(group);
        });
    }

    /* ---------- STEPPER NAVIGATION ---------- */
    function updateStepper() {
        const steps = $$('.step');
        steps.forEach((step, i) => {
            step.classList.remove('active', 'completed');
            if (i < currentStep) step.classList.add('completed');
            if (i === currentStep) step.classList.add('active');
        });

        const progress = currentStep / (totalSteps - 1) * 100;
        dom.stepperProgress.style.width = progress + '%';

        $$('.form-panel').forEach((panel, i) => {
            panel.classList.toggle('active', i === currentStep);
        });

        dom.btnPrev.disabled = currentStep === 0;
        dom.btnNext.classList.toggle('hidden', currentStep === totalSteps - 1);
        dom.btnSubmit.classList.toggle('hidden', currentStep !== totalSteps - 1);

        if (currentStep === totalSteps - 1) renderReview();
    }

    function goToStep(step) {
        if (step < 0 || step >= totalSteps) return;
        currentStep = step;
        updateStepper();
        dom.formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /* ---------- API CALL ---------- */
    async function submitPrediction() {
        const data = collectFormData();

        dom.loadingOverlay.classList.remove('hidden');

        try {
            const res = await fetch(API.predict, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || 'Erreur ' + res.status);
            }

            const result = await res.json();
            showResult(result);
        } catch (e) {
            alert('Erreur: ' + e.message);
        } finally {
            dom.loadingOverlay.classList.add('hidden');
        }
    }

    /* ---------- RESULT DISPLAY ---------- */
    function showResult(result) {
        dom.formSection.classList.add('hidden');
        dom.resultSection.classList.remove('hidden');

        const prob = result.probability;
        const pct = (prob * 100).toFixed(1);

        // Gauge animation
        const arcLength = 251.33;
        const offset = arcLength * (1 - prob);
        dom.gaugeFill.style.strokeDashoffset = arcLength; // reset
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                dom.gaugeFill.style.strokeDashoffset = offset;
            });
        });

        // Gauge color
        let color;
        if (prob < 0.3) color = 'var(--success)';
        else if (prob < 0.6) color = 'var(--warning)';
        else color = 'var(--danger)';
        dom.gaugeFill.style.stroke = color;

        // Animate counter
        animateCounter(dom.gaugeValue, 0, parseFloat(pct), 1000);

        // Badge
        dom.resultBadge.className = 'result-badge';
        if (prob < 0.3) {
            dom.resultBadge.classList.add('badge-success');
            dom.resultLabel.textContent = 'Stable';
        } else if (prob < 0.6) {
            dom.resultBadge.classList.add('badge-warning');
            dom.resultLabel.textContent = 'Risque modere';
        } else {
            dom.resultBadge.classList.add('badge-danger');
            dom.resultLabel.textContent = 'Risque de depart';
        }

        // Interpretation
        const interps = [
            { max: 0.2, text: 'Risque tres faible. Cet employe presente un profil stable avec des indicateurs tres positifs. Aucune action corrective n\'est necessaire.' },
            { max: 0.4, text: 'Risque faible. Le profil est globalement rassurant. Un suivi de routine est recommande pour maintenir cet engagement.' },
            { max: 0.6, text: 'Risque modere. Certains indicateurs meritent une attention particuliere. Un entretien individuel pourrait aider a identifier les axes d\'amelioration.' },
            { max: 0.8, text: 'Risque eleve. Plusieurs facteurs indiquent un potentiel depart. Des mesures correctives rapides sont recommandees : revue salariale, mobilite interne, ou plan de retention.' },
            { max: 1.01, text: 'Risque critique. Le profil presente de nombreux signaux d\'alerte. Une intervention immediate est necessaire pour retenir cet employe.' },
        ];
        dom.resultInterp.textContent = interps.find(i => prob < i.max).text;

        dom.resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function animateCounter(el, from, to, duration) {
        const start = performance.now();
        function tick(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            const val = from + (to - from) * eased;
            el.textContent = val.toFixed(1) + '%';
            if (progress < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    /* ---------- NAVIGATION SECTION MANAGEMENT ---------- */
    function showHero() {
        dom.hero.classList.remove('hidden');
        dom.formSection.classList.add('hidden');
        dom.resultSection.classList.add('hidden');
    }

    function showForm() {
        dom.hero.classList.add('hidden');
        dom.formSection.classList.remove('hidden');
        dom.resultSection.classList.add('hidden');
        currentStep = 0;
        updateStepper();
    }

    function resetForm() {
        // Reset all fields to defaults
        Object.values(FIELDS).flat().forEach(field => {
            switch (field.type) {
                case 'number':
                case 'select':
                case 'slider': {
                    const el = document.getElementById('f-' + field.key);
                    if (el) el.value = field.default;
                    // Update slider display
                    if (field.type === 'slider') {
                        const valSpan = el.parentElement.querySelector('.slider-value');
                        if (valSpan) valSpan.textContent = field.default + (field.unit || '');
                    }
                    break;
                }
                case 'rating': {
                    const group = document.querySelector(`.rating-group[data-key="${field.key}"]`);
                    if (group) {
                        group.querySelectorAll('.rating-btn').forEach(btn => {
                            btn.classList.toggle('active', parseInt(btn.dataset.value) === field.default);
                        });
                    }
                    break;
                }
                case 'toggle': {
                    const toggle = document.querySelector(`.toggle[data-key="${field.key}"]`);
                    if (toggle) {
                        const isOn = field.default === toggle.dataset.on;
                        toggle.classList.toggle('active', isOn);
                        const label = toggle.nextElementSibling;
                        if (label) label.textContent = field.default;
                    }
                    break;
                }
            }
        });

        // Reset gauge
        dom.gaugeFill.style.strokeDashoffset = 251.33;
        dom.gaugeValue.textContent = '0%';
    }

    /* ---------- INIT ---------- */
    function init() {
        initTheme();
        checkHealth();
        renderAllFields();

        // Hero → Form
        dom.startBtn.addEventListener('click', showForm);

        // Stepper navigation
        dom.btnPrev.addEventListener('click', () => goToStep(currentStep - 1));
        dom.btnNext.addEventListener('click', () => goToStep(currentStep + 1));

        // Stepper direct click
        $$('.step').forEach(step => {
            step.addEventListener('click', () => {
                const target = parseInt(step.dataset.step);
                if (target <= currentStep) goToStep(target);
            });
        });

        // Submit
        dom.btnSubmit.addEventListener('click', submitPrediction);

        // New analysis
        dom.btnNew.addEventListener('click', () => {
            resetForm();
            showForm();
        });
    }

    // Start
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
