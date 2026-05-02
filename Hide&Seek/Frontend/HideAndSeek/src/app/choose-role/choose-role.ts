import { Component } from '@angular/core';
import { Router, RouterLink } from "@angular/router";

@Component({
  selector: 'app-choose-role',
  imports: [],
  templateUrl: './choose-role.html',
  styleUrl: './choose-role.css',
})
export class ChooseRole {

  role: 'hider' | 'seeker' | null = null;

  constructor(private router: Router) {
    this.role = null;
  }

  chooseRole(selectedRole: 'hider' | 'seeker') {
    this.role = selectedRole;
    // TODO: You can add additional logic here, such as navigating to a different page or updating the UI based on the selected role.
    this.router.navigate(['/get-map-size']);
  }

}
