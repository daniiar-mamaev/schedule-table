const { createApp } = Vue;

createApp({
    created() {
        this.fetchSchedule();
        this.fetchPeople();
    },
    methods: {
        async addPerson() {
            const person = prompt("Enter name:");
            if (!person) return;
            const response = await fetch("/api/person/add", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ person }),
            });
            if (response.ok) {
                this.people.push(person);
            }
        },
        async fetchPeople() {
            const response = await fetch("/api/people");
            const data = await response.json();
            this.people = Object.values(data.people);
        },
        async fetchSchedule() {
            const response = await fetch("/api/schedule");
            const data = await response.json();
            this.blocks = data.blocks;
        },
        startDrag(person, day) {
            this.dragging = true;
            this.dragStart = { person, day };
        },
        endDrag(person, day, personIndex) {
            if (!this.dragging) return;
            this.dragging = false;
            const task = prompt("Enter task:");
            if (!task) return;
            this.newBlock = {
                _id: personIndex,
                person,
                task,
                start_day: this.dragStart.day,
                end_day: day,
            };
            this.addTask(this.newBlock);
        },
        isBlock(person, day) {
            return this.blocks.some(
                (block) => block.person === person && this.isInRange(block, day)
            );
        },
        isInRange(block, day) {
            const dayOrder = this.days.indexOf(day);
            const startOrder = this.days.indexOf(block.start_day);
            const endOrder = this.days.indexOf(block.end_day);
            return dayOrder >= startOrder && dayOrder <= endOrder;
        },
        getTask(person, day) {
            const block = this.blocks.find(
                (block) => block.person === person && this.isInRange(block, day)
            );
            return block || null;
        },
        async addTask(newBlock) {
            const response = await fetch("/api/task/add", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(newBlock),
            });
            const data = await response.json();
            console.log(data.message);
        },
        openModal(task) {
            this.selectedTask = task;
            this.showModal = true;
            console.log(this.selectedTask);
        },
        async saveAndClose() {
            console.log(this.selectedTask);
            const response = fetch("/api/task/edit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(this.selectedTask),
            });
            window.location.reload();
        },
    },
    data() {
        return {
            people: [],
            days: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            blocks: [],
            dragging: false,
            dragStart: null,
            newBlock: null,
            showModal: false,
            selectedTask: null,
            person: "",
        };
    },
}).mount("#app");
