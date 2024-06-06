const { createApp } = Vue;

const Modal = {
    props: ["show", "onClose"],
    emits: ["update:show"],
    template: "#modal-template",
    methods: {
        close() {
            this.$emit("update:show", false);
        },
        async addNewTask() {
            this.task = document.getElementById("task").value;
            this.person = document.getElementById("person").value;
            this.start_day = document.getElementById("start_day").value;
            this.end_day = document.getElementById("end_day").value;
            if (
                !this.task ||
                !this.person ||
                !this.start_day ||
                !this.end_day
            ) {
                alert("Please fill all fields");
                return;
            }
            this.showModal = false;

            const response = await fetch("/task/add", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    task: this.task,
                    person: this.person,
                    start_day: this.start_day,
                    end_day: this.end_day,
                }),
            });
            if (!response.ok) {
                console.error("Failed to add task");
            }
        },
    },
    data() {
        return {
            days: ["Mon", "Tue", "Wed", "Thu", "Fri"],
            task: "",
            person: "",
            start_day: "",
            end_day: "",
        };
    },
};

createApp({
    components: {
        Modal,
    },
    created() {
        this.fetchSchedule();
    },
    methods: {
        async fetchSchedule() {
            const response = await fetch("/schedule");
            const data = await response.json();
            this.blocks = data.blocks;
            console.log(this.blocks);
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
                body: JSON.stringify({ person }),
            });
            if (response.ok) {
                this.people.push({ id: response.id, person });
            }
        },
        getTask(person, day) {
            const block = this.blocks.find(
                (block) => block.person === person && this.isInRange(block, day)
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
                (block) => block.person === person && this.isInRange(block, day)
            );
        },
        isInRange(block, day) {
            const dayOrder = this.days.indexOf(day);
            const startOrder = this.days.indexOf(block.start_day);
            const endOrder = this.days.indexOf(block.end_day);
            return dayOrder >= startOrder && dayOrder <= endOrder;
        },

        openAddTaskModal() {
            this.showModal = true;
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
            newBlock: null,
            showModal: false,
            selectedTask: null,
            people: [],
        };
    },
}).mount("#app");
