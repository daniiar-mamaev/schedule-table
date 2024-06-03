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
            this.blocks.push(this.newBlock);
            this.saveSchedule();
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
            return block ? block.task : "";
        },
        async saveSchedule() {
            const response = await fetch("/api/schedule", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ blocks: this.blocks }),
            });
            const data = await response.json();
            console.log(data.message);
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
        };
    },
}).mount("#app");
