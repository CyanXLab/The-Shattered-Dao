// 逆仙录·天道残卷 - 主入口
window.addEventListener('DOMContentLoaded', async () => {
  console.log('逆仙录·天道残卷 - 启动中...');
  try {
    await Auth.init();
    console.log('游戏已加载');
    setTimeout(() => UI.toast('欢迎来到逆仙录！点击地图移动，点击建筑进入。', 'info'), 500);
    setTimeout(() => UI.toast('提示：先打开行囊，使用青木诀玉简学习功法', 'info'), 3000);
  } catch (e) {
    console.error('启动失败:', e);
    document.getElementById('loading').textContent = '启动失败：' + e.message;
  }
});

window.addEventListener('keydown', (e) => {
  if (UI.state && UI.state.player && !UI.state.player.in_combat) {
    if (document.getElementById('modal-overlay').style.display !== 'none') return;
    if (document.getElementById('combat-overlay').style.display !== 'none') return;
    let dir = null;
    if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') dir = 'up';
    else if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') dir = 'down';
    else if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') dir = 'left';
    else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') dir = 'right';
    if (dir) {
      e.preventDefault();
      API.move(dir).then(r => {
        UI.refresh();
        if (r.action === 'gather' && r.resource_id) {
          API.gather(r.resource_id).then(g => { UI.toast(g.msg, g.ok ? 'success' : 'error'); UI.refresh(); });
        } else if (r.action === 'combat') UI.refresh();
        else if (r.action === 'talk') UI.openNPCDialog(r.npc_id);
        else if (r.action) UI.handleBuildingAction(r);
        else if (r.msg) UI.toast(r.msg, 'info');
      });
    }
  }
  if (e.key === 'Escape') {
    if (document.getElementById('combat-overlay').style.display === 'none') UI.closeModal();
  }
});
