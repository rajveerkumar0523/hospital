
// ======================================
// Load Previous Symptom Analysis
// ======================================

const savedData = JSON.parse(

    sessionStorage.getItem("symptomData")

);

if (savedData) {

    const symptomBox = document.getElementById("symptoms");

    if (symptomBox) {

        symptomBox.value = savedData.symptoms;

    }

}


// ===============================
// Elements
// ===============================

const form = document.getElementById("recommendationForm");

const textarea = document.getElementById("symptoms");

const chips = document.querySelectorAll(".symptom-chip");

const emptyState = document.getElementById("emptyState");

const loadingState = document.getElementById("loadingState");

const resultState = document.getElementById("resultState");


// ===============================
// Symptom Chips
// ===============================

chips.forEach((chip) => {

    chip.addEventListener("click", () => {

        chip.classList.toggle("active");

        const symptoms = [];

        document
            .querySelectorAll(".symptom-chip.active")
            .forEach((item) => {

                symptoms.push(
                    item.innerText.replace(/^[^\w]+/, "").trim()
                );

            });

        textarea.value = symptoms.join(", ");

    });

});


// ===============================
// Form Submit
// ===============================

form.addEventListener("submit", async function (e) {

    e.preventDefault();

    emptyState.style.display = "none";
    resultState.style.display = "none";
    loadingState.style.display = "flex";

    const formData = new FormData(form);

    try {

        const response = await fetch(
            "/ai/api/appointment-recommendation/",
            {
                method: "POST",
                headers: {
                    "X-CSRFToken":
                        document.querySelector(
                            "[name=csrfmiddlewaretoken]"
                        ).value,
                },
                body: formData,
            }
        );

        const data = await response.json();

        loadingState.style.display = "none";

        if (!data.success) {

            alert("AI Recommendation Failed.");

            emptyState.style.display = "flex";

            return;

        }

        showResult(data.result);

    }

    catch (err) {

        console.error(err);

        loadingState.style.display = "none";

        emptyState.style.display = "flex";

        alert("Server Error");

    }

});


// ===============================
// Show Result
// ===============================

function showResult(result) {

    resultState.style.display = "block";

    document.getElementById(
        "departmentName"
    ).innerText =
        result.department || "-";

    document.getElementById(
        "doctorName"
    ).innerText =
        result.doctor || "No Doctor Available";

    bookBtn.dataset.doctorId = result.doctor_id;

    document.getElementById(
        "aiReason"
    ).innerText =
        result.reason || "-";

    const badge = document.getElementById(
        "priorityBadge"
    );

    badge.innerText =
        result.priority || "Medium";

    badge.classList.remove(
        "priority-low",
        "priority-medium",
        "priority-high"
    );

    switch ((result.priority || "").toLowerCase()) {

        case "low":

            badge.classList.add(
                "priority-low"
            );

            break;

        case "medium":

            badge.classList.add(
                "priority-medium"
            );

            break;

        case "high":

            badge.classList.add(
                "priority-high"
            );

            break;

    }

}


// ===============================
// Book Appointment
// ===============================

const bookBtn = document.querySelector(".book-btn");

bookBtn.addEventListener("click", () => {

    const doctorId = bookBtn.dataset.doctorId;

    if (!doctorId) {
        alert("No doctor available.");
        return;
    }

    window.location.href = `/appointments/book/${doctorId}/`;

});