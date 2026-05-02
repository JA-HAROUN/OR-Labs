import { Component } from '@angular/core';
import { NgClass } from '@angular/common';
import { Router } from '@angular/router';
import { MapSizeService } from '../services/map-size.service';

@Component({
  selector: 'app-get-map-size',
  imports: [],
  templateUrl: './get-map-size.html',
  styleUrl: './get-map-size.css',
})
export class GetMapSize {
  
  rows: number | null = null;
  columns: number | null = null;

  constructor(private router: Router, private mapSize: MapSizeService) {
    this.rows = null;
    this.columns = null;
  }

  generateMatrix() {
    this.mapSize.setSize(this.rows || 0, this.columns || 0);
    this.router.navigate(['/game-page']);
  }
  changeRole() {
    // TODO: navigate to the role selection page
    this.router.navigate(['/choose-role']);
  }
}
