class TextToSpeech {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.audioElement = new Audio();
        this.isPlaying = false;
        this.apiUrl = 'https://api.sws.speechify.com/v1/audio/stream';
        this.isLoading = false;
        this.isInitialized = false;
    }

    async initialize(htmlContent) {
        if (this.isInitialized) {
            console.log('TextToSpeech already initialized');
            return;
        }
        console.log('Initializing TextToSpeech');
        const textContent = this.extractTextFromHtml(htmlContent);
        await this.loadAudio(textContent);
        this.isInitialized = true;
        console.log('TextToSpeech initialization complete');
    }

    extractTextFromHtml(htmlContent) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, 'text/html');

        const textElements = doc.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, blockquote, td, th');
        
        const allText = Array.from(textElements)
            .map(el => el.textContent.trim())
            .filter(text => text.length > 0)
            .join('. ');

        console.log('Extracted text length:', allText.length);
        return allText;
    }

    async loadAudio(textContent) {
        try {
            this.isLoading = true;
            console.log('Loading audio for text of length:', textContent.length);
            const audioBlob = await this.getAudioStream(textContent);
            const audioUrl = URL.createObjectURL(audioBlob);
            this.audioElement.src = audioUrl;
            this.isLoading = false;
            console.log('Audio loaded successfully');
        } catch (error) {
            this.isLoading = false;
            console.error('Error loading audio:', error);
            throw error;
        }
    }

    async playPause() {
        if (this.isLoading) {
            console.log('Still loading, please wait');
            return this.isPlaying;
        }

        try {
            if (this.isPlaying) {
                this.audioElement.pause();
                this.isPlaying = false;
                console.log('Audio paused');
            } else {
                await this.audioElement.play();
                this.isPlaying = true;
                console.log('Audio playing');
            }
            return this.isPlaying;
        } catch (error) {
            console.error('Error in playPause:', error);
            throw error;
        }
    }

    async getAudioStream(text) {
        try {
            console.log('Sending text to API, length:', text.length);
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': this.apiKey,
                    'Accept': '*/*'
                },
                body: JSON.stringify({
                    voice_id: "henry",
                    input: text,
                    model: "simba-multilingual"
                })
            });

            if (!response.ok) {
                const errorBody = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, body: ${errorBody}`);
            }

            console.log('Received audio stream from API');
            return await response.blob();
        } catch (error) {
            console.error('Error fetching audio stream:', error);
            throw error;
        }
    }
}

// Make TextToSpeech available globally
window.TextToSpeech = TextToSpeech;