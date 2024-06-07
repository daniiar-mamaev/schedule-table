const { createApp } = Vue;

const updateTask = {
    props: ["show", "onClose", "opened_task_id"],
    emits: ["update:show"],
    template: "#modal-template",
    methods: {
        close() {
            this.$emit("update:show", false);
        },
        async updateTask() {
            this.task_id = this.opened_task_id;
            this.task = document.getElementById("task").value;
            this.start_day = document.getElementById("start_day").value;
            this.end_day = document.getElementById("end_day").value;
            if (!this.task || !this.start_day || !this.end_day) {
                alert("Please fill all fields");
                return;
            }

            const response = await fetch("/task/update", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    task_id: this.task_id,
                    task: this.task,
                    start_day: this.start_day,
                    end_day: this.end_day,
                }),
            });
        },
    },
    data() {
        return {
            days: ["Mon", "Tue", "Wed", "Thu", "Fri"],
            task_id: "",
            task: "",
            start_day: "",
            end_day: "",
        };
    },
};

createApp({
    components: {
        updateTask,
    },
    created() {
        this.fetchSchedule();
    },
    methods: {
        async fetchSchedule() {
            const response = await fetch("/schedule");
            const data = await response.json();
            this.blocks = data.task_list;
            this.blocks.forEach((block) => {
                this.people.push({ id: block._id, person: block.person });
            });
        },
        async addPerson() {
            const person = prompt("Enter person's name:");
            if (!person) return;
            const response = await fetch("/person/add", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ name: person }),
            });
            if (!response.ok) {
                console.error("Failed to add person");
            }
        },
        getTask(person, day) {
            const block = this.blocks.find(
                (block) => block.person === person.person
            );
            return block || null;
        },
        startDrag(person, day) {
            this.dragging = true;
            this.dragStart = { person, day };
        },
        endDrag(person, day, personIndex) {
            if (!this.dragging) return;
            this.dragging = false;
            this.showModal = true;
        },
        isBlock(person, day) {
            return this.blocks.some(
                (block) =>
                    block.person === person.person && this.isInRange(block, day)
            );
        },
        isInRange(block, day) {
            const dayOrder = this.days.indexOf(day);
            const startOrder = this.days.indexOf(block.start_day);
            const endOrder = this.days.indexOf(block.end_day);
            return dayOrder >= startOrder && dayOrder <= endOrder;
        },
        openModal(task) {
            this.showModal = true;
            this.opened_task_id = task._id;
        },
        closeModal() {
            this.showModal = false;
        },
    },
    data() {
        return {
            days: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            blocks: [],
            dragging: false,
            dragStart: null,
            showModal: false,
            opened_task_id: null,
            people: [],
        };
    },
}).mount("#app");
