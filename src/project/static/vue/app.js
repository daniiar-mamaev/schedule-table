const { createApp } = Vue;

createApp({
    created() {
        this.fetchSchedule();
    },
    methods: {
        async fetchSchedule() {
            const response = await fetch("/api/schedule");
            const data = await response.json();
            this.blocks = data.blocks;
        },
        startDrag(person, day) {
            this.dragging = true;
            this.dragStart = { person, day };
        },
        endDrag(person, day) {
            if (!this.dragging) return;
            this.dragging = false;
            const task = prompt("Enter task:");
            if (!task) return;
            this.newBlock = {
                person,
                task,
                start_day: this.dragStart.day,
                end_day: day,
            };
            this.saveSchedule(this.newBlock);
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
        async saveSchedule(newBlock) {
            const response = await fetch("/api/schedule", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(newBlock),
            });
            window.location.reload();
            const data = await response.json();
            console.log(data.message);
        },
        openModal(task) {
            this.selectedTask = task;
            this.showModal = true;
            console.log(this.selectedTask);
        },
        saveAndClose() {
            // Save the task to the database here...
            this.showModal = false;
        },
    },
    data() {
        return {
            people: ["Anton", "Oleg", "Ivan", "Petr"],
            days: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            blocks: [],
            dragging: false,
            dragStart: null,
            newBlock: null,
            showModal: false,
            selectedTask: null,
        };
    },
}).mount("#app");
