console.log("app.js loaded");

// =============================
// CONFIG
// =============================

const BASE_URL = "http://127.0.0.1:8000";

let categoryMap={};

let editingErrorId = null;
// =============================
// LOGIN
// =============================

async function login(event){

    event.preventDefault();

    const email = document.getElementById("email").value;

    const password = document.getElementById("password").value;

    try{

        const response = await fetch(`${BASE_URL}/auth/login`,{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                email,
                password
            })

        });

        const data = await response.json();

        console.log("Status:",response.status);
        console.log("Data",data);

        if(!response.ok){

            alert(data.detail);

            return;

        }

        // Save JWT

        localStorage.setItem("token",data.access_token);

        console.log("Token after save:",localStorage.getItem("token"));

        // Redirect

        window.location.href="dashboard.html";

    }

    catch(err){

        console.log(err);

        alert("Unable to connect to server.");

    }

}



// =============================
// LOGOUT
// =============================

function logout(){

    localStorage.removeItem("token");

    window.location.href="index.html";

}

// REGISTER

async function registerUser(event){

    event.preventDefault();

    const data={
        username:document.getElementById("name").value,
        email:document.getElementById("email").value,
        password:document.getElementById("password").value
    };

    const response=await fetch(
        `${BASE_URL}/auth/register`,
        {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify(data)
        }
    );

    const result=await response.json();
    
    if(response.ok){
        // alert("Registration Successful");

        console.log("Redirect line reached");

        window.location.href="index.html";
    }
    else{
        alert(result.detail);
    }
}

// =============================
// LOAD DASHBOARD
// =============================

async function loadDashboard(){

    const token = localStorage.getItem("token");

    if(!token){

        window.location.href="index.html";

        return;

    }

    try{

        // ---------------- User ----------------

        const userResponse = await fetch(`${BASE_URL}/auth/me`,{

            headers:{
                Authorization:`Bearer ${token}`
            }

        });

        if(userResponse.status===401){

            logout();

            return;

        }

        const user = await userResponse.json();

        document.getElementById("username").innerHTML=user.username;



        // ---------------- Dashboard ----------------

        const dashboardResponse=await fetch(`${BASE_URL}/dashboard`,{

            headers:{
                Authorization:`Bearer ${token}`
            }

        });

        const dashboard=await dashboardResponse.json();

        console.log("FULL DASHBOARD:", dashboard);
        console.log("RECENT ERRORS:", dashboard.recent_errors);
        console.log("CATEGORY FROM BROWSER:", dashboard.recent_errors[0].category);

        document.getElementById("totalErrors").innerHTML=dashboard.total_errors;

        document.getElementById("totalCategories").innerHTML=dashboard.total_categories;

        document.getElementById("openIssues").innerHTML=dashboard.open_issues;

        document.getElementById("resolvedIssues").innerHTML=dashboard.resolved_issues;



        // LOAD RECENT ERRORS
        // ==========================

        console.log(dashboard);
        const errors=dashboard.recent_errors;

        console.log("RECENT ERRORS:", errors);
        console.log("CATEGORY:", errors[0]?.category);

        let html="";

        errors.forEach(error=>{

            let badge = "";

            if (error.status === "Open") {

                badge = `<span class="status status-open">Open</span>`;

            }
            else if (error.status === "Resolved") {

                badge = `<span class="status status-resolved">Resolved</span>`;

            }
            else {

                badge = `<span class="status status-progress">${error.status}</span>`;

            }

            html+=`

            <tr>

                <td>${error.error}</td>
                <td>${error.category||"-"}</td>
                <td>${badge}</td>
                <td>

                    <button class="table-btn" onclick="viewError(${error.id})">

                        View

                    </button>

                </td>

            </tr>

            `;

        });

        document.getElementById("recentErrorsTable").innerHTML=html;

    }

    catch(err){

        console.log(err);

        alert("Unable to load dashboard.");

    }

}

function openAddModal(){
    
    editingErrorId=null;
    document.getElementById("addErrorForm").reset();
    document.querySelector("#addModal h2").innerHTML="Add Known Error";
    document.querySelector("#addErrorForm button[type='submit']").innerHTML="Save Known Error";
    document.getElementById("addModal").style.display="flex";
}

function closeAddModal(){
    document.getElementById("addModal").style.display="none";
}

window.onclick=function(event){
    const modal=this.document.getElementById("addModal");
    if(event.target==modal){
        modal.style.display="none";
    }
}

async function createKnownError(event){

    event.preventDefault();

    const token = localStorage.getItem("token");

    const body = {

        title: document.getElementById("title").value,

        application: document.getElementById("application").value,

        category_id: parseInt(document.getElementById("category").value),

        symptoms: document.getElementById("symptoms").value,

        root_cause: document.getElementById("rootCause").value,

        workaround: document.getElementById("workaround").value,

        resolution: document.getElementById("resolution").value,

        status: "Open"

    };

    let url = `${BASE_URL}/known-errors/`;
    let method = "POST";

    if(editingErrorId != null){

        url = `${BASE_URL}/known-errors/${editingErrorId}`;
        method = "PUT";
    }

    const response = await fetch(url,{

        method: method,

        headers:{
            "Content-Type":"application/json",
            Authorization:`Bearer ${token}`
        },

        body: JSON.stringify(body)

    });

    const data = await response.json();

    if(!response.ok){

        alert(data.detail || "Unable to save.");

        return;
    }

    alert(
        editingErrorId == null ?
        "Known Error Created Successfully" :
        "Known Error Updated Successfully"
    );

    editingErrorId = null;

    document.getElementById("addErrorForm").reset();

    document.querySelector("#addModal h2").innerHTML =
    "Add Known Error";

    document.querySelector("#addErrorForm button[type='submit']").innerHTML =
    "Save Known Error";

    closeAddModal();

    loadKnownErrors();
}

async function loadCategories(){

    const token=localStorage.getItem("token");

    const response=await fetch(`${BASE_URL}/categories`,{
        headers:{
            Authorization:`Bearer ${token}`
        }
    });

    const categories=await response.json();

    const dropdown=document.getElementById("category");

    dropdown.innerHTML=`<option value="">Select Category</option>`;

    categoryMap={};

    categories.forEach(category=>{

        categoryMap[category.id]=category.name;

        dropdown.innerHTML += `

        <option value="${category.id}">

            ${category.name}

        </option>

        `;

    });
}

async function loadKnownErrors(){

    await loadCategories();

    const token = localStorage.getItem("token");

    const response = await fetch(`${BASE_URL}/known-errors`,{

        headers:{

            Authorization:`Bearer ${token}`

        }

    });

    const errors = await response.json();

    loadApplicationFilter(errors);
    loadCategoryFilter(errors);

    let html="";

    errors.forEach(error=>{

        let badge="";

        if(error.status=="Open"){

            badge=`<span class="status-open">Open</span>`;

        }

        else if(error.status=="Resolved"){

            badge=`<span class="status-resolved">Resolved</span>`;

        }

        else{

            badge=`<span class="status-progress">${error.status}</span>`;

        }

        html+=`

        <tr>

        <td>${error.title}</td>

        <td>${error.application}</td>

        <td>${categoryMap[error.category_id]}</td>

        <td>${badge}</td>

        <td>

        <button class="view-btn" onclick="viewError(${error.id})">
            <i class="fa fa-eye"></i>
        </button>

        <button class="edit-btn" onclick="editError(${error.id})">
            <i class="fa fa-pen"></i>
        </button>

        <button class="delete-btn" onclick="deleteError(${error.id})">
            <i class="fa fa-trash"></i>
        </button>

        </td>

        </tr>

        `;

    });

    document.getElementById("knownErrorsTable").innerHTML=html;

}


async function askAI(){

    const token = localStorage.getItem("token");

    const question = document.getElementById("question").value.trim();

    if(question===""){

        alert("Please enter your issue.");

        return;

    }

    const responseBox=document.getElementById("aiResponse");

    responseBox.innerHTML=`

        <div class="loading">

            🤖 AI is analysing your issue...

        </div>

    `;

    try{

        const response=await fetch(`${BASE_URL}/ai/chat`,{

            method:"POST",

            headers:{
                "Content-Type":"application/json",
                Authorization:`Bearer ${token}`
            },

            body:JSON.stringify({
                question:question
            })

        });

        const data=await response.json();

        let confidence="low";
        let confidenceText="LOW";

        if(data.similarity>=0.90){

            confidence="high";
            confidenceText="HIGH";

        }

        else if(data.similarity>=0.70){

            confidence="medium";
            confidenceText="MEDIUM";

        }

        let statusClass="status-open";

        if(data.known_error.status==="Resolved"){

            statusClass="status-resolved";

        }

        else if(data.known_error.status==="In Progress"){

            statusClass="status-progress";

        }

        responseBox.innerHTML = `

<div class="ai-report">

    <div class="report-header">

        <h3>🤖 AI Incident Analysis</h3>

        <span class="match-badge">

            🟡 ${(data.similarity * 100).toFixed(1)}% Match

        </span>

    </div>

    <table class="incident-table">

        <tr>

            <th>Error</th>

            <td>${data.known_error.title}</td>

        </tr>

        <tr>

            <th>Category</th>

            <td>${data.known_error.category||"-"}</td>

        </tr>

        <tr>

            <th>Status</th>

            <td>

                <span class="status ${statusClass}">

                    ${data.known_error.status}

                </span>

            </td>

        </tr>

        <tr class="root-row">

            <th>Root Cause</th>

            <td>${data.known_error.root_cause}</td>

        </tr>

        <tr class="action-row">

            <th>Recommended Action</th>

            <td>${data.known_error.workaround}</td>

        </tr>

    </table>

    <div class="summary-box">

        <h4>💬 AI Recommendation</h4>

        <p>${data.answer}</p>

    </div>

</div>

`;

    }

    catch(error){

        console.error("AI Error:", error);

        responseBox.innerHTML=`

    <div class="ai-response">

    <h3>Error</h3>

    <p>${error}</p>

    </div>

    `;

    }

}

async function viewError(id){

    const token=localStorage.getItem("token");
    
    try{

        const response=await fetch(
            `${BASE_URL}/known-errors/${id}`,
            {
                headers:{
                    Authorization:`Bearer ${token}`
                }
            }
        );

        const error=await response.json();

        if(!response.ok){

            alert(error.detail||"Unable to load known error details.");
            return;
        }

        document.getElementById("modalTitle").textContent=error.title;
        document.getElementById("modalBody").innerHTML=`

            <div class="error-summary-grid">

                <div class="detail-card">

                    <span class="detail-label">
                        <i class="fa-solid fa-folder"></i>
                        Category
                    </span>

                    <p class="detail-value">
                        ${error.category || "Not available"}
                    </p>

                </div>


                <div class="detail-card">

                    <span class="detail-label">
                        <i class="fa-solid fa-circle-info"></i>
                        Status
                    </span>

                    <p>
                        <span class="status-detail ${
                            error.status === "Resolved"
                                ? "resolved"
                                : error.status === "In Progress"
                                ? "in-progress"
                                : "open"
                        }">

                            ${error.status || "Open"}

                        </span>
                    </p>

                </div>

            </div>


            <div class="detail-section">

                <div class="detail-section-title">

                    <i class="fa-solid fa-triangle-exclamation"></i>

                    Symptoms

                </div>

                <p>
                    ${error.symptoms || "Not available"}
                </p>

            </div>


            <div class="detail-section">

                <div class="detail-section-title">

                    <i class="fa-solid fa-magnifying-glass"></i>

                    Root Cause

                </div>

                <p>
                    ${error.root_cause || "Not available"}
                </p>

            </div>


            <div class="detail-section workaround-section">

                <div class="detail-section-title">

                    <i class="fa-solid fa-screwdriver-wrench"></i>

                    Workaround

                </div>

                <p>
                    ${error.workaround || "Not available"}
                </p>

            </div>


            <div class="detail-section resolution-section">

                <div class="detail-section-title">

                    <i class="fa-solid fa-circle-check"></i>

                    Resolution

                </div>

                <p>
                    ${error.resolution || "Not available"}
                </p>

            </div>

        `;
        document.getElementById("viewModal").style.display="flex";

    }
    catch(error){
        console.log("View Error:",error);
        alert("Unable to load known error details.");
    }
}


function closeViewModal(){
    document.getElementById("viewModal").style.display="none";
}


async function editError(id){

    const token = localStorage.getItem("token");

    const response = await fetch(`${BASE_URL}/known-errors/${id}`,{
        headers:{
            Authorization:`Bearer ${token}`
        }
    });

    const error = await response.json();

    editingErrorId = id;

    document.getElementById("title").value = error.title;
    document.getElementById("application").value = error.application;
    document.getElementById("category").value = error.category_id;
    document.getElementById("symptoms").value = error.symptoms;
    document.getElementById("rootCause").value = error.root_cause;
    document.getElementById("workaround").value = error.workaround;
    document.getElementById("resolution").value = error.resolution;

    document.querySelector("#addModal h2").innerHTML = "Edit Known Error";

    document.querySelector("#addModal button[type='submit']").innerHTML =
    "Update Known Error";

    openAddModal();

}


async function deleteError(id){

    const confirmDelete=confirm("Are you sure you want to delete this Known Error?");

    if(!confirmDelete){
        return;
    }

    const token=localStorage.getItem("token");

    try{

        const response=await fetch(
            `${BASE_URL}/known-errors/${id}`,
            {
                method:"DELETE",
                headers:{
                    Authorization:`Bearer ${token}`
                }
            }
        );

        const data=await response.json();

        if(!response.ok){
            alert(data.detail||"Unable to detect the Known Error");
            return;
        }

        alert(data.message||"Known Error deleted successfully.");

        loadKnownErrors();
    }
    catch(error){
        console.error("Delete error",error);

        alert("Unable to connect to the server.");
    }
}

function filterErrors(){

    const searchText = document
        .getElementById("search")
        .value
        .toLowerCase()
        .trim();

    const rows = document.querySelectorAll(
        "#knownErrorsTable tr"
    );

    rows.forEach(row => {

        const title =
            row.cells[0].textContent.toLowerCase();

        const application =
            row.cells[1].textContent.toLowerCase();

        const matches =
            title.includes(searchText) ||
            application.includes(searchText);

        row.style.display = matches ? "" : "none";

    });

}


function loadApplicationFilter(errors){
    const applicationFilter=document.getElementById("applicationFilter");
    applicationFilter.innerHTML=`<option value="">All Applications</option>`;

    const applications=[
        ...new Set(
            errors.map(error=>error.application)
        )
    ];

    applications.forEach(application=>{
        applicationFilter.innerHTML+=`
        <option value="${application}">${application}</option>`;
    });
}

function filterByApplication(){
    const selectedApplication =
        document.getElementById("applicationFilter").value;

    const rows = document.querySelectorAll(
        "#knownErrorsTable tr"
    );

    rows.forEach(row => {

        const application =
            row.cells[1].textContent.trim();

        const matches =
            selectedApplication === "" ||
            application === selectedApplication;

        row.style.display =
            matches ? "" : "none";

    });
}


function loadCategoryFilter(errors) {

    const categoryFilter =
        document.getElementById("categoryFilter");

    categoryFilter.innerHTML =
        `<option value="">All Categories</option>`;

    const categories = [
        ...new Set(
            errors.map(error => categoryMap[error.category_id])
        )
    ];

    categories.forEach(category => {

        categoryFilter.innerHTML += `
            <option value="${category}">
                ${category}
            </option>
        `;

    });
}


function filterCategory() {

    const selectedCategory =
        document.getElementById("categoryFilter").value;

    const rows = document.querySelectorAll(
        "#knownErrorsTable tr"
    );

    rows.forEach(row => {

        const category =
            row.cells[2].textContent.trim();

        const matches =
            selectedCategory === "" ||
            category === selectedCategory;

        row.style.display =
            matches ? "" : "none";

    });
}


function filterStatus() {

    const selectedStatus =
        document.getElementById("statusFilter").value;

    const rows = document.querySelectorAll(
        "#knownErrorsTable tr"
    );

    rows.forEach(row => {

        const status =
            row.cells[3].textContent.trim();

        const matches =
            selectedStatus === "" ||
            status === selectedStatus;

        row.style.display =
            matches ? "" : "none";

    });
}

function renderCategories(categories){

    let html="";
    categories.forEach(category=>{
        
        html+=`
        <tr>
            <td>${category.name}</td>
            <td>${category.description}</td>
            <td>

                <button class="view-btn"
                    onclick="editCategory(${category.id})">

                    <i class="fa fa-pen"></i>

                </button>

                <button class="delete-btn"
                    onclick="deleteCategory(${category.id})">

                    <i class="fa fa-trash"></i>

                </button>

            </td>
        </tr>
        `;

    });

    document.getElementById("categoriesTable").innerHTML=html;
}


function openCategoryModal() {

    editingCategoryId = null;

    document.getElementById("categoryForm").reset();

    document.getElementById("categoryModalTitle").innerHTML =
        "Add Category";

    document.getElementById("categorySaveBtn").innerHTML =
        "Save Category";

    document.getElementById("categoryModal").style.display = "flex";

}

function closeCategoryModal() {

    document.getElementById("categoryModal").style.display = "none";

}


async function saveCategory(event) {

    event.preventDefault();

    const token = localStorage.getItem("token");

    const body = {

        name: document.getElementById("categoryName").value,

        description: document.getElementById("categoryDescription").value

    };

    let url = `${BASE_URL}/categories/`;

    let method = "POST";

    if (editingCategoryId != null) {

        url = `${BASE_URL}/categories/${editingCategoryId}`;

        method = "PUT";

    }

    const response = await fetch(url, {

        method: method,

        headers: {

            "Content-Type": "application/json",

            Authorization: `Bearer ${token}`

        },

        body: JSON.stringify(body)

    });

    const data = await response.json();

    if (!response.ok) {

        alert(data.detail);

        return;

    }

    alert(

        editingCategoryId == null

            ? "Category Created Successfully"

            : "Category Updated Successfully"

    );

    editingCategoryId = null;

    closeCategoryModal();

    loadCategoriesPage();

}


async function editCategory(id) {

    const token = localStorage.getItem("token");

    try {

        const response = await fetch(
            `${BASE_URL}/categories/${id}`,
            {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            }
        );

        const category = await response.json();

        if (!response.ok) {

            alert(
                category.detail ||
                "Unable to load category."
            );

            return;
        }

        console.log("Category received:", category);

        // Store ID of category being edited
        editingCategoryId = id;

        // Put existing values into form
        document.getElementById("categoryName").value =
            category.name || "";

        document.getElementById("categoryDescription").value =
            category.description || "";

        // Change modal title
        document.getElementById("categoryModalTitle").textContent =
            "Edit Category";

        // Change button text
        document.getElementById("categorySaveBtn").textContent =
            "Update Category";

        // Open modal
        document.getElementById("categoryModal").style.display =
            "flex";

    }

    catch (error) {

        console.error("Edit Category Error:", error);

        alert("Unable to load category.");

    }
}


async function deleteCategory(id) {

    const confirmDelete = confirm(
        "Delete this category?"
    );

    if (!confirmDelete)
        return;

    const token = localStorage.getItem("token");

    const response = await fetch(`${BASE_URL}/categories/${id}`, {

        method: "DELETE",

        headers: {

            Authorization: `Bearer ${token}`

        }

    });

    const data = await response.json();

    if (!response.ok) {

        alert(data.detail);

        return;

    }

    alert("Category Deleted Successfully");

    loadCategoriesPage();

}


function filterCategories() {

    const text = document
        .getElementById("categorySearch")
        .value
        .toLowerCase();

    const filtered = allCategories.filter(category =>

        category.name.toLowerCase().includes(text) ||

        category.description.toLowerCase().includes(text)

    );

    renderCategories(filtered);

}


window.onclick = function(event) {

    const modal = document.getElementById("categoryModal");

    if (event.target == modal) {

        closeCategoryModal();

    }

}



let allCategories = [];

async function loadCategoriesPage() {

    const token = localStorage.getItem("token");

    if (!token) {
        window.location.href = "index.html";
        return;
    }

    try {

        const response = await fetch(`${BASE_URL}/categories/`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        const categories = await response.json();

        console.log(categories);

        allCategories = categories;

        let html = "";

        categories.forEach(category => {

            html += `
                <tr>

                    <td>${category.name}</td>

                    <td>${category.description}</td>

                    <td>

                        <button class="edit-btn" onclick="editCategory(${category.id})">
                            <i class="fa fa-pen"></i>
                        </button>

                        <button class="delete-btn" onclick="deleteCategory(${category.id})">
                            <i class="fa fa-trash"></i>
                        </button>

                    </td>

                </tr>
            `;

        });

        document.getElementById("categoriesTable").innerHTML = html;

    }

    catch(err){

        console.log(err);

        alert("Unable to load categories.");

    }

}




