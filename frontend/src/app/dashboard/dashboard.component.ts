import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../api.service';



@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, AfterViewInit {
  username: string = '';

  nickname: string = '';
  nombre: string = '';
  descripcion: string = '';
  rutaFotoPerfil: string = '';
  description: string = '';
  lenguajeSeleccionado: string = '';

  constructor(private route: ActivatedRoute, private api: ApiService) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {

      this.username = params.get('username')!;
    });
  }

  ngAfterViewInit(): void {
    this.api.getProfile(this.username).subscribe({
      next: (response) => {
        if ('nickname' in response) {
          this.nickname = response.nickname;
        }

        if ('nombre' in response) {
          this.nombre = response.nombre;
        }
        if ('description' in response) {
          this.descripcion = response.description;
        }

        if ('rutaFotoPerfil' in response) {
          this.rutaFotoPerfil = response.rutaFotoPerfil;
        }

        if ('descripcion' in response) {
          this.description = response.descripcion;
        }

        if ('message' in response) {
          alert(response.message);
        }
      },
      error: (error) => {
        alert(error.error.message);
      }
    });

  }
  leerDescripcion(lenguaje: string): void {
    // Asignar el lenguaje seleccionado a la variable
    this.lenguajeSeleccionado = lenguaje;
    this.api.speak({ target_language: this.lenguajeSeleccionado, text: this.descripcion }).subscribe({
      next: (response) => {
        this.api.speak({ text: this.descripcion, target_language: this.lenguajeSeleccionado }).subscribe({
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