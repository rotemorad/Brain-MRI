Node: fsl
=========


 Hierarchy : _flirt0
 Exec ID : _flirt0


Original Inputs
---------------


* angle_rep : <undefined>
* apply_isoxfm : <undefined>
* apply_xfm : <undefined>
* args : <undefined>
* bbrslope : <undefined>
* bbrtype : <undefined>
* bgvalue : <undefined>
* bins : <undefined>
* coarse_search : <undefined>
* cost : <undefined>
* cost_func : <undefined>
* datatype : <undefined>
* display_init : <undefined>
* dof : 12
* echospacing : <undefined>
* environ : {'FSLOUTPUTTYPE': 'NIFTI_GZ'}
* fieldmap : <undefined>
* fieldmapmask : <undefined>
* fine_search : <undefined>
* force_scaling : <undefined>
* in_file : /mnt/z/Rotem_Orad/scripts/Brain-MRI/tbss/tbss1/prepfa/mapflow/_prepfa0/DTI__FA_prep.nii.gz
* in_matrix_file : <undefined>
* in_weight : /mnt/z/Rotem_Orad/scripts/Brain-MRI/tbss/tbss1/getmask2/mapflow/_getmask20/DTI__FA_prep_mask_maths.nii.gz
* interp : <undefined>
* min_sampling : <undefined>
* no_clamp : <undefined>
* no_resample : <undefined>
* no_resample_blur : <undefined>
* no_search : <undefined>
* out_file : <undefined>
* out_log : <undefined>
* out_matrix_file : <undefined>
* output_type : NIFTI_GZ
* padding_size : <undefined>
* pedir : <undefined>
* ref_weight : <undefined>
* reference : /usr/local/fsl/data/standard/FMRIB58_FA_1mm.nii.gz
* rigid2D : <undefined>
* save_log : <undefined>
* schedule : <undefined>
* searchr_x : <undefined>
* searchr_y : <undefined>
* searchr_z : <undefined>
* sinc_width : <undefined>
* sinc_window : <undefined>
* uses_qform : <undefined>
* verbose : <undefined>
* wm_seg : <undefined>
* wmcoords : <undefined>
* wmnorms : <undefined>


Execution Inputs
----------------


* angle_rep : <undefined>
* apply_isoxfm : <undefined>
* apply_xfm : <undefined>
* args : <undefined>
* bbrslope : <undefined>
* bbrtype : <undefined>
* bgvalue : <undefined>
* bins : <undefined>
* coarse_search : <undefined>
* cost : <undefined>
* cost_func : <undefined>
* datatype : <undefined>
* display_init : <undefined>
* dof : 12
* echospacing : <undefined>
* environ : {'FSLOUTPUTTYPE': 'NIFTI_GZ'}
* fieldmap : <undefined>
* fieldmapmask : <undefined>
* fine_search : <undefined>
* force_scaling : <undefined>
* in_file : /mnt/z/Rotem_Orad/scripts/Brain-MRI/tbss/tbss1/prepfa/mapflow/_prepfa0/DTI__FA_prep.nii.gz
* in_matrix_file : <undefined>
* in_weight : /mnt/z/Rotem_Orad/scripts/Brain-MRI/tbss/tbss1/getmask2/mapflow/_getmask20/DTI__FA_prep_mask_maths.nii.gz
* interp : <undefined>
* min_sampling : <undefined>
* no_clamp : <undefined>
* no_resample : <undefined>
* no_resample_blur : <undefined>
* no_search : <undefined>
* out_file : <undefined>
* out_log : <undefined>
* out_matrix_file : <undefined>
* output_type : NIFTI_GZ
* padding_size : <undefined>
* pedir : <undefined>
* ref_weight : <undefined>
* reference : /usr/local/fsl/data/standard/FMRIB58_FA_1mm.nii.gz
* rigid2D : <undefined>
* save_log : <undefined>
* schedule : <undefined>
* searchr_x : <undefined>
* searchr_y : <undefined>
* searchr_z : <undefined>
* sinc_width : <undefined>
* sinc_window : <undefined>
* uses_qform : <undefined>
* verbose : <undefined>
* wm_seg : <undefined>
* wmcoords : <undefined>
* wmnorms : <undefined>


Execution Outputs
-----------------


* out_file : <undefined>
* out_log : <undefined>
* out_matrix_file : /mnt/z/Rotem_Orad/scripts/Brain-MRI/tbss/tbss2/flirt/mapflow/_flirt0/DTI__FA_prep_flirt.mat


Runtime info
------------


* cmdline : flirt -in /mnt/z/Rotem_Orad/scripts/Brain-MRI/tbss/tbss1/prepfa/mapflow/_prepfa0/DTI__FA_prep.nii.gz -ref /usr/local/fsl/data/standard/FMRIB58_FA_1mm.nii.gz -out DTI__FA_prep_flirt.nii.gz -omat DTI__FA_prep_flirt.mat -dof 12 -inweight /mnt/z/Rotem_Orad/scripts/Brain-MRI/tbss/tbss1/getmask2/mapflow/_getmask20/DTI__FA_prep_mask_maths.nii.gz
* duration : 23.237012
* hostname : fmri-rotem
* prev_wd : /mnt/z/Rotem_Orad/scripts/PhD/tbss
* working_dir : /mnt/z/Rotem_Orad/scripts/Brain-MRI/tbss/tbss2/flirt/mapflow/_flirt0


Terminal output
~~~~~~~~~~~~~~~


 


Terminal - standard output
~~~~~~~~~~~~~~~~~~~~~~~~~~


 


Terminal - standard error
~~~~~~~~~~~~~~~~~~~~~~~~~


 


Environment
~~~~~~~~~~~


* COLORTERM : truecolor
* DISPLAY : 172.26.144.1:0
* FREESURFER_HOME : /usr/local/freesurfer/7.3.2
* FSLDIR : /usr/local/fsl
* FSLGECUDAQ : cuda.q
* FSLLOCKDIR : 
* FSLMACHINELIST : 
* FSLMULTIFILEQUIT : TRUE
* FSLOUTPUTTYPE : NIFTI_GZ
* FSLREMOTECALL : 
* FSLTCLSH : /usr/local/fsl/bin/fsltclsh
* FSLWISH : /usr/local/fsl/bin/fslwish
* GIT_ASKPASS : /root/.vscode-server/bin/6c3e3dba23e8fadc360aed75ce363ba185c49794/extensions/git/dist/askpass.sh
* HOME : /home/fsluser
* HOSTTYPE : x86_64
* LANG : en_US.UTF-8
* LESSCLOSE : /usr/bin/lesspipe %s %s
* LESSOPEN : | /usr/bin/lesspipe %s
* LIBGL_ALWAYS_INDIRECT : 1
* LOGNAME : fsluser
* LS_COLORS : rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:*.xz=01;31:*.zst=01;31:*.tzst=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.wim=01;31:*.swm=01;31:*.dwm=01;31:*.esd=01;31:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:
* MAIL : /var/mail/fsluser
* NAME : fmri-rotem
* PATH : /usr/local/fsl/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
* PWD : /mnt/z/Rotem_Orad/scripts/Brain-MRI
* SHELL : /bin/bash
* SHLVL : 2
* TERM : xterm-256color
* TERM_PROGRAM : vscode
* TERM_PROGRAM_VERSION : 1.81.1
* USER : fsluser
* VSCODE_GIT_ASKPASS_EXTRA_ARGS : 
* VSCODE_GIT_ASKPASS_MAIN : /root/.vscode-server/bin/6c3e3dba23e8fadc360aed75ce363ba185c49794/extensions/git/dist/askpass-main.js
* VSCODE_GIT_ASKPASS_NODE : /root/.vscode-server/bin/6c3e3dba23e8fadc360aed75ce363ba185c49794/node
* VSCODE_GIT_IPC_HANDLE : /tmp/vscode-git-061c107fa9.sock
* VSCODE_IPC_HOOK_CLI : /tmp/vscode-ipc-6947a23b-bd76-4ad3-963f-b9830617117f.sock
* WSLENV : VSCODE_WSL_EXT_LOCATION/up
* WSL_DISTRO_NAME : Ubuntu-22.04-fsl
* WSL_INTEROP : /run/WSL/31265_interop
* XDG_DATA_DIRS : /usr/local/share:/usr/share:/var/lib/snapd/desktop
* _ : /usr/bin/python

