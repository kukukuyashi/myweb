// 全局音乐播放器
class GlobalMusicPlayer {
    constructor() {
        this.audioElement = null;
        this.currentTrack = -1;
        this.isPlaying = false;
        this.volume = 0.8;
        this.tracks = [];
        this.init();
    }
    
    init() {
        // 创建音频元素
        this.audioElement = document.createElement('audio');
        this.audioElement.style.display = 'none';
        document.body.appendChild(this.audioElement);
        
        // 加载曲目
        this.loadTracks();
        
        // 设置音量
        const savedVolume = localStorage.getItem('musicVolume');
        if (savedVolume) {
            this.volume = parseFloat(savedVolume);
        }
        this.audioElement.volume = this.volume;
        
        // 监听音频事件
        this.audioElement.addEventListener('ended', () => {
            this.playNext();
        });
        
        this.audioElement.addEventListener('pause', () => {
            this.isPlaying = false;
            this.saveState();
        });
        
        this.audioElement.addEventListener('play', () => {
            this.isPlaying = true;
            this.saveState();
        });
        
        // 监听页面卸载事件，确保状态保存
        window.addEventListener('beforeunload', () => {
            this.saveState();
        });
        
        // 加载播放状态
        this.loadState();
    }
    
    loadTracks() {
        // 检测当前页面位置，动态生成音乐文件路径
        const currentPath = window.location.pathname;
        const isContentDir = currentPath.includes('/Content/');
        
        const pathPrefix = isContentDir ? '../Music/' : 'Music/';
        
        // 音乐文件路径
        const musicFiles = [
            pathPrefix + 'SANABI/SANBAI OST  Ending Means Starting Again.mp3',
            pathPrefix + '[Hi-Res][241013]TVアニメ『らんま1／2』EDテーマ「あんたなんて。」／りりあ。[48kHz／24bit][FLAC]/01.あんたなんて。.flac',
            pathPrefix + '小林家的龙女仆/愛のシュプリーム!.flac',
            pathPrefix + '[Hi-Res][260123]映画『超かぐや姫！』オリジナル・サウンドトラック[48kHz／24bit][FLAC]/30.IROHA\'S Dancing All Night.flac',
            pathPrefix + '[Hi-Res][260123]映画『超かぐや姫！』オリジナル・サウンドトラック[48kHz／24bit][FLAC]/33.ヤチヨ絵巻.flac'
        ];
        
        // 曲目信息
        const trackInfo = [
            { title: 'Ending Means Starting Again', artist: 'SANABI OST', album: 'SANABI' },
            { title: 'あんたなんて。', artist: 'りりあ。', album: 'らんま1／2 EDテーマ' },
            { title: '愛のシュプリーム!', artist: '小林家的龙女仆', album: '小林家的龙女仆 OST' },
            { title: 'IROHA\'S Dancing All Night', artist: '超かぐや姫！', album: '超かぐや姫！ OST' },
            { title: 'ヤチヨ絵巻', artist: '超かぐや姫！', album: '超かぐや姫！ OST' }
        ];
        
        this.tracks = musicFiles.map((file, index) => ({
            file: file,
            ...trackInfo[index]
        }));
    }
    
    playTrack(index) {
        if (index >= 0 && index < this.tracks.length) {
            this.currentTrack = index;
            this.audioElement.src = this.tracks[index].file;
            this.audioElement.play().catch(e => {
                console.log('Auto-play prevented:', e);
                this.isPlaying = false;
            });
            this.isPlaying = true;
            this.saveState();
        }
    }
    
    playPause() {
        if (this.currentTrack === -1) {
            // 没有选择曲目，默认播放第一首
            this.playTrack(0);
        } else {
            if (this.isPlaying) {
                this.audioElement.pause();
            } else {
                this.audioElement.play().catch(e => {
                    console.log('Play prevented:', e);
                    this.isPlaying = false;
                });
            }
        }
    }
    
    stop() {
        this.audioElement.pause();
        this.audioElement.currentTime = 0;
        this.isPlaying = false;
        this.saveState();
    }
    
    playNext() {
        if (this.currentTrack < this.tracks.length - 1) {
            this.playTrack(this.currentTrack + 1);
        } else {
            // 循环播放
            this.playTrack(0);
        }
    }
    
    playPrevious() {
        if (this.currentTrack > 0) {
            this.playTrack(this.currentTrack - 1);
        } else {
            // 循环播放
            this.playTrack(this.tracks.length - 1);
        }
    }
    
    setVolume(volume) {
        this.volume = volume;
        this.audioElement.volume = volume;
        localStorage.setItem('musicVolume', volume);
    }
    
    saveState() {
        const state = {
            currentTrack: this.currentTrack,
            isPlaying: this.isPlaying,
            currentTime: this.audioElement.currentTime
        };
        sessionStorage.setItem('musicPlayerState', JSON.stringify(state));
    }
    
    loadState() {
        const savedState = sessionStorage.getItem('musicPlayerState');
        if (savedState) {
            try {
                const state = JSON.parse(savedState);
                this.currentTrack = state.currentTrack;
                this.isPlaying = state.isPlaying;
                const currentTime = state.currentTime || 0;
                
                if (this.currentTrack >= 0 && this.currentTrack < this.tracks.length) {
                    const currentSrc = this.audioElement.src;
                    const newSrc = this.tracks[this.currentTrack].file;
                    
                    // 只有当音频源不同时才重新设置src
                    if (!currentSrc || !currentSrc.includes(newSrc)) {
                        this.audioElement.src = newSrc;
                        
                        // 等待音频加载完成后再设置currentTime和播放状态
                        this.audioElement.addEventListener('loadedmetadata', () => {
                            this.audioElement.currentTime = currentTime;
                            
                            if (this.isPlaying) {
                                this.audioElement.play().catch(e => {
                                    console.log('Auto-play prevented:', e);
                                    this.isPlaying = false;
                                });
                            }
                        }, { once: true });
                    } else {
                        // 音频源相同，直接设置currentTime和播放状态
                        this.audioElement.currentTime = currentTime;
                        
                        if (this.isPlaying) {
                            this.audioElement.play().catch(e => {
                                console.log('Auto-play prevented:', e);
                                this.isPlaying = false;
                            });
                        }
                    }
                }
            } catch (e) {
                console.error('Error loading music player state:', e);
            }
        }
    }
    
    getCurrentTrack() {
        if (this.currentTrack >= 0 && this.currentTrack < this.tracks.length) {
            return this.tracks[this.currentTrack];
        }
        return null;
    }
    
    getTracks() {
        return this.tracks;
    }
}

// 初始化全局播放器
let globalMusicPlayer = null;

document.addEventListener('DOMContentLoaded', function() {
    if (!window.globalMusicPlayer) {
        window.globalMusicPlayer = new GlobalMusicPlayer();
    }
});