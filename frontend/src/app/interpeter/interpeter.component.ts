import { Component } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-interpeter',
  templateUrl: './interpeter.component.html',
  styleUrls: ['./interpeter.component.scss']
})
export class InterpeterComponent {
  text: string = '';
  language: string = '';

  constructor(private api: ApiService) { }

  translate() {
    this.api.translate({ target_language: this.language, text: this.text }).subscribe({
      next: (response) => {
        this.api.speak({ text: response.translated_text, target_language: response.translated_text }).subscribe({
          next: (response) => {
            const audio = response.audio_base64;
            const audioElement = new Audio(`data:audio/mp3;base64,${audio}`);
            audioElement.play();
          },
          error: (error) => {
            alert(error.error.message);
          }
        });
      },
      error: (error) => {
        alert(error.error.message);
      }
    });
  }
}
