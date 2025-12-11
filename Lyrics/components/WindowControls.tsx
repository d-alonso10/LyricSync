import React from 'react';

const WindowControls: React.FC = () => {
  const handleMinimize = () => {
    if (window.require) {
      const { ipcRenderer } = window.require('electron');
      ipcRenderer.send('minimize-window');
    }
  };

  const handleClose = () => {
    if (window.require) {
      const { ipcRenderer } = window.require('electron');
      ipcRenderer.send('close-window');
    } else {
      window.close();
    }
  };

  return (
    <div className="absolute top-0 left-0 w-full h-10 z-50 flex items-center px-4 app-draggable">

      <div className="flex gap-2 p-2 rounded-lg transition-colors cursor-default no-drag hover:bg-black/10">

        <div
          onClick={handleClose}
          className="w-3 h-3 rounded-full bg-[#FF5F57] border border-[#E0443E] shadow-sm flex items-center justify-center overflow-hidden group/btn cursor-pointer"
        >
          <svg className="w-2 h-2 text-black/50 opacity-0 group-hover:opacity-100 group-hover/btn:opacity-100" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="4">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </div>

        <div
          onClick={handleMinimize}
          className="w-3 h-3 rounded-full bg-[#FEBC2E] border border-[#D89E24] shadow-sm flex items-center justify-center overflow-hidden group/btn cursor-pointer"
        >
          <svg className="w-2 h-2 text-black/50 opacity-0 group-hover:opacity-100 group-hover/btn:opacity-100" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="4">
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </div>
      </div>
    </div>
  );
};

export default WindowControls;