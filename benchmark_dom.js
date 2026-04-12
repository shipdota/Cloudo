class ClassList {
    constructor() { this.classes = new Set(); }
    add(c) { this.classes.add(c); }
    remove(c) { this.classes.delete(c); }
    contains(c) { return this.classes.has(c); }
}

class Element {
    constructor(tag) {
        this.tag = tag;
        this.classList = new ClassList();
        this.style = {};
        this.children = [];
        this.parent = null;
    }
    appendChild(child) {
        this.children.push(child);
        child.parent = this;
    }
    remove() {
        if (this.parent) {
            this.parent.children = this.parent.children.filter(c => c !== this);
            this.parent = null;
        }
    }
    addEventListener() {}
}

const document = {
    createElement: (tag) => new Element(tag)
};

const ITERATIONS = 1000000;

function benchmarkCreation() {
    const gameArea = new Element('div');
    gameArea.clientWidth = 800;
    gameArea.clientHeight = 600;
    let activeTarget = null;

    const start = performance.now();
    for (let i = 0; i < ITERATIONS; i++) {
        if (activeTarget) activeTarget.remove();

        const target = document.createElement('div');
        target.classList.add('target');

        const maxX = gameArea.clientWidth - 50;
        const maxY = gameArea.clientHeight - 50;
        const randomX = Math.floor(Math.random() * maxX);
        const randomY = Math.floor(Math.random() * maxY);

        target.style.left = `${randomX}px`;
        target.style.top = `${randomY}px`;
        target.addEventListener('mousedown', () => {});

        gameArea.appendChild(target);
        activeTarget = target;
    }
    if (activeTarget) activeTarget.remove();
    return performance.now() - start;
}

function benchmarkPooling() {
    const gameArea = new Element('div');
    gameArea.clientWidth = 800;
    gameArea.clientHeight = 600;

    const pooledTarget = document.createElement('div');
    pooledTarget.classList.add('target');
    pooledTarget.classList.add('hidden');
    pooledTarget.addEventListener('mousedown', () => {});
    gameArea.appendChild(pooledTarget);

    let activeTarget = null;

    const start = performance.now();
    for (let i = 0; i < ITERATIONS; i++) {
        if (activeTarget) {
            activeTarget.classList.add('hidden');
        }

        const maxX = gameArea.clientWidth - 50;
        const maxY = gameArea.clientHeight - 50;
        const randomX = Math.floor(Math.random() * maxX);
        const randomY = Math.floor(Math.random() * maxY);

        pooledTarget.style.left = `${randomX}px`;
        pooledTarget.style.top = `${randomY}px`;
        pooledTarget.classList.remove('hidden');

        activeTarget = pooledTarget;
    }
    if (activeTarget) {
        activeTarget.classList.add('hidden');
    }
    return performance.now() - start;
}

const timeCreation = benchmarkCreation();
const timePooling = benchmarkPooling();

console.log(`Creation method: ${timeCreation.toFixed(2)}ms`);
console.log(`Pooling method: ${timePooling.toFixed(2)}ms`);
console.log(`Improvement: ${((timeCreation - timePooling) / timeCreation * 100).toFixed(2)}%`);
