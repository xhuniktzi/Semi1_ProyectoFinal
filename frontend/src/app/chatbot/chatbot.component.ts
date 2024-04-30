import { Component } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.scss']
})
export class ChatbotComponent {
  message_list: { message: string, sender: string }[] = [];
  message: string = '';

  constructor(private api: ApiService) { }

  sendMessage() {
    this.message_list.push({ message: this.message, sender: 'user' });
    this.api.chat(this.message).subscribe({
      next: (response) => {
        this.message_list.push({ message: response.message, sender: 'bot' });
      },
      error: (error) => {
        this.message_list.push({ message: `${error.error.message}`, sender: 'system' });
      }
    });
    this.message = '';
  }
}
