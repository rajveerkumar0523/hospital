console.log("AI Symptom Checker Loaded");

// ======================================
// Elements
// ======================================

const form = document.getElementById("symptomForm");

const textarea = document.getElementById("symptoms");

const chips = document.querySelectorAll(".symptom-chip");

const emptyState = document.getElementById("emptyState");

const loadingState = document.getElementById("loadingState");

const resultState = document.getElementById("resultState");


// ======================================
// Symptom Chips
// ======================================

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


// ======================================
// Submit Form
// ======================================

form.addEventListener("submit", async function (e) {

    e.preventDefault();

    emptyState.style.display = "none";

    resultState.style.display = "none";

    loadingState.style.display = "block";

    const formData = new FormData(form);

    try {

        const response = await fetch(

            "/ai/api/symptom-checker/",

            {

                method: "POST",

                headers: {

                    "X-CSRFToken":
                        document.querySelector(
                            "[name=csrfmiddlewaretoken]"
                        ).value

                },

                body: formData

            }

        );

        const data = await response.json();

        loadingState.style.display = "none";

        if (!data.success) {

            alert("AI analysis failed.");

            emptyState.style.display = "block";

            return;

        }

        showResult(data.result);
        document.getElementById(

    "continueBtn"

).style.display = "inline-block";

    }

    catch (error) {

        console.error(error);

        loadingState.style.display = "none";

        emptyState.style.display = "block";

        alert("Server Error");

    }

});


// ======================================
// Result
// ======================================

function showResult(result) {

    resultState.style.display = "block";

    document.getElementById(
        "departmentName"
    ).innerText =
        result.department || "-";

    document.getElementById(
        "priorityBadge"
    ).innerText =
        result.priority || "Medium";

    document.getElementById(
        "disclaimer"
    ).innerText =
        result.disclaimer || "";



    fillList(

        "conditionList",

        result.possible_conditions

    );


    fillList(

        "careList",

        result.home_care

    );


    fillList(

        "warningList",

        result.emergency_warning

    );



    updatePriority(

        result.priority

    );


    // Save data for Appointment Recommendation

sessionStorage.setItem(

    "symptomData",

    JSON.stringify({

        symptoms: textarea.value,

        department: result.department,

        priority: result.priority

    })

);

}



// ======================================
// Fill List
// ======================================

function fillList(id, items) {

    const ul = document.getElementById(id);

    ul.innerHTML = "";

    if (!items || items.length === 0) {

        ul.innerHTML = "<li>Not Available</li>";

        return;

    }

    items.forEach((item) => {

        const li = document.createElement("li");

        li.innerText = item;

        ul.appendChild(li);

    });

}



// ======================================
// Priority Color
// ======================================

function updatePriority(priority) {

    const badge = document.getElementById(

        "priorityBadge"

    );

    badge.className = "";

    switch ((priority || "").toLowerCase()) {

        case "low":

            badge.style.background = "#22c55e";

            badge.style.color = "#fff";

            break;

        case "medium":

            badge.style.background = "#facc15";

            badge.style.color = "#111";

            break;

        case "high":

            badge.style.background = "#ef4444";

            badge.style.color = "#fff";

            break;

    }

}

