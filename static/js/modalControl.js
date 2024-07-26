// 关闭模态框
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'none';
    const backdrop = document.getElementById('modal-backdrop');
    if (backdrop) {
        backdrop.remove();
    }
}

// 打开模态框
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'block';

    // 创建并添加背景遮罩层
    const backdrop = document.createElement('div');
    backdrop.id = 'modal-backdrop';
    backdrop.onclick = () => closeModal(modalId); // 点击遮罩层关闭模态框
    document.body.appendChild(backdrop);

    // 关闭按钮绑定事件
    const closeButtons = modal.querySelectorAll('[data-dismiss="modal"]');
    closeButtons.forEach(button => {
        button.onclick = () => closeModal(modalId);
    });
}

// 绑定打开模态框的按钮事件
document.addEventListener('DOMContentLoaded', () => {
    const openButtons = document.querySelectorAll('[data-toggle="modal"]');
    openButtons.forEach(button => {
        const targetId = button.getAttribute('data-target').substring(1);
        button.onclick = () => openModal(targetId);
    });
});
